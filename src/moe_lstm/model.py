"""LSTM mixture of experts. TensorFlow is imported inside the builder.

The experts are LSTMs that read one window. This is not a Transformer mixture
and the gate does not route token by token. The study default keeps the top
expert only. ``top_k=None`` is the dense softmax over every expert.
"""

from __future__ import annotations

from moe_lstm.constants import AUX_LOSS_WEIGHT, EXPERT_UNITS, N_EXPERTS, TOP_K

_LAYER_CACHE: dict[str, type] = {}


def renormalized_top_k(probs, k: int, n_experts: int):
    """Keep the ``k`` largest router probabilities and renormalize them.

    Every other expert is exactly 0. The kept weights sum to 1.
    """
    from keras import ops

    if k < 1 or k >= n_experts:
        raise ValueError(
            f"k must be between 1 and {n_experts - 1} so the gate can drop an expert. Got {k}."
        )
    _values, indices = ops.top_k(probs, k=k)
    mask = ops.one_hot(indices, n_experts)
    # one_hot on the index axis is (batch, k, n_experts).
    # The choice of experts is discrete. Gradients flow through the kept probabilities.
    mask = ops.stop_gradient(ops.cast(ops.sum(mask, axis=1), dtype=probs.dtype))
    selected = probs * mask
    denom = ops.sum(selected, axis=-1, keepdims=True)
    return selected / ops.maximum(denom, ops.cast(1e-9, dtype=probs.dtype))


def switch_auxiliary_loss(router_probs, k: int, n_experts: int):
    """Switch load-balancing term ``n * sum(f_i * P_i)``.

    ``P`` is the mean router probability. ``f`` is the fraction of windows
    whose top-k includes that expert. The minimum is 1 when both are uniform.
    """
    from keras import ops

    if k < 1 or k >= n_experts:
        raise ValueError(
            f"k must be between 1 and {n_experts - 1} for the dispatch fractions. Got {k}."
        )
    _values, indices = ops.top_k(router_probs, k=k)
    dispatch = ops.cast(ops.sum(ops.one_hot(indices, n_experts), axis=1), dtype=router_probs.dtype)
    # Dispatch is the hard assignment. The penalty trains the router probabilities.
    dispatch = ops.stop_gradient(dispatch)
    fraction = ops.mean(dispatch, axis=0)
    fraction = fraction / ops.sum(fraction)
    importance = ops.mean(router_probs, axis=0)
    width = ops.cast(n_experts, dtype=router_probs.dtype)
    return width * ops.sum(fraction * importance)


def _gate_layers() -> tuple[type, type]:
    """Build the Keras layers on first use so importing this module skips TensorFlow."""
    cached_gate = _LAYER_CACHE.get("TopKGate")
    cached_balance = _LAYER_CACHE.get("LoadBalance")
    if cached_gate is not None and cached_balance is not None:
        return cached_gate, cached_balance

    from tensorflow.keras.layers import Layer

    class TopKGate(Layer):
        def __init__(self, k: int, n_experts: int, **kwargs):
            super().__init__(**kwargs)
            self.k = int(k)
            self.n_experts = int(n_experts)

        def call(self, probs):
            return renormalized_top_k(probs, self.k, self.n_experts)

        def get_config(self):
            config = super().get_config()
            config.update({"k": self.k, "n_experts": self.n_experts})
            return config

    class LoadBalance(Layer):
        """Identity on the router. Adds the Switch auxiliary term while training."""

        def __init__(self, k: int, n_experts: int, aux_weight: float, **kwargs):
            super().__init__(**kwargs)
            self.k = int(k)
            self.n_experts = int(n_experts)
            self.aux_weight = float(aux_weight)

        def call(self, probs):
            self.add_loss(self.aux_weight * switch_auxiliary_loss(probs, self.k, self.n_experts))
            return probs

        def get_config(self):
            config = super().get_config()
            config.update({"k": self.k, "n_experts": self.n_experts, "aux_weight": self.aux_weight})
            return config

    _LAYER_CACHE["TopKGate"] = TopKGate
    _LAYER_CACHE["LoadBalance"] = LoadBalance
    return TopKGate, LoadBalance


def _require_count(name: str, value: int, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}. Got {value!r}.")
    return value


def build_moe_model(
    lookback: int,
    n_features: int,
    n_experts: int = N_EXPERTS,
    expert_units: int = EXPERT_UNITS,
    top_k: int | None = TOP_K,
    aux_loss_weight: float | None = None,
):
    """Three LSTM experts, a router on the last bar, and a sigmoid head.

    ``top_k`` selects that many experts and renormalizes their router
    probabilities. The others contribute 0. ``top_k=None`` is the dense
    softmax over every expert. The default is ``TOP_K`` (1).

    ``aux_loss_weight=None`` uses ``AUX_LOSS_WEIGHT`` on the sparse path and
    0 on the dense path. A positive weight on the dense path is an error.
    The auxiliary term is a Switch load-balancing loss added beside binary
    crossentropy. The model still has one output.
    """
    import tensorflow.keras.backend as K
    from tensorflow.keras.layers import LSTM, Dense, Flatten, Input, Lambda
    from tensorflow.keras.models import Model

    lookback = _require_count("lookback", lookback, 1)
    n_features = _require_count("n_features", n_features, 1)
    n_experts = _require_count("n_experts", n_experts, 2)
    expert_units = _require_count("expert_units", expert_units, 1)
    if top_k is not None:
        top_k = _require_count("top_k", top_k, 1)
        if top_k >= n_experts:
            raise ValueError(
                f"top_k must be between 1 and {n_experts - 1} for a sparse gate, "
                f"or None for the dense softmax. Got {top_k}."
            )
    if aux_loss_weight is None:
        aux_loss_weight = AUX_LOSS_WEIGHT if top_k is not None else 0.0
    if isinstance(aux_loss_weight, bool) or not isinstance(aux_loss_weight, (int, float)):
        raise ValueError(f"aux_loss_weight must be a nonnegative number. Got {aux_loss_weight!r}.")
    aux_loss_weight = float(aux_loss_weight)
    if aux_loss_weight < 0 or aux_loss_weight != aux_loss_weight or aux_loss_weight == float("inf"):
        raise ValueError(f"aux_loss_weight must be a nonnegative finite number. Got {aux_loss_weight}.")
    if aux_loss_weight > 0 and top_k is None:
        raise ValueError(
            "aux_loss_weight applies to the sparse top-k path. "
            "Pass top_k, or leave the auxiliary weight at 0 for the dense softmax."
        )

    inputs = Input(shape=(lookback, n_features), name="Input_Sequence")
    experts = []
    for index in range(1, n_experts + 1):
        sequence = LSTM(expert_units, return_sequences=True, name=f"LSTM_Expert_{index}")(inputs)
        experts.append(Flatten(name=f"Flatten_Expert_{index}")(sequence))
    router = Dense(n_experts, activation="softmax", name="Gating_Network")(inputs[:, -1, :])
    if top_k is not None and aux_loss_weight > 0:
        _top_k_gate, load_balance = _gate_layers()
        router = load_balance(
            k=top_k,
            n_experts=n_experts,
            aux_weight=aux_loss_weight,
            name="Load_Balance",
        )(router)
    if top_k is None:
        gate = router
    else:
        top_k_gate, _load_balance = _gate_layers()
        gate = top_k_gate(k=top_k, n_experts=n_experts, name="Sparse_Gate")(router)
    # Stack experts on a new axis so the gate weights can scale them.
    # Concatenating on the feature axis cannot broadcast against that gate.
    stacked = Lambda(lambda tensors: K.stack(tensors, axis=1), name="Stack_Experts")(experts)
    weighted = Lambda(
        lambda pair: K.sum(pair[0] * K.expand_dims(pair[1], axis=-1), axis=1),
        name="Weighted_Sum",
    )([stacked, gate])
    output = Dense(1, activation="sigmoid", name="Final_Output")(weighted)
    model = Model(inputs=inputs, outputs=output, name="MOE_LSTM_Model")
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model
