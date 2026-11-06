"""LSTM mixture of experts. TensorFlow is imported inside the builder."""

def build_moe_model(lookback: int, n_features: int):
    import tensorflow.keras.backend as K
    from tensorflow.keras.layers import LSTM, Dense, Flatten, Input, Lambda
    from tensorflow.keras.models import Model

    inputs = Input(shape=(lookback, n_features), name="Input_Sequence")
    experts = []
    for index in range(1, 4):
        sequence = LSTM(64, return_sequences=True, name=f"LSTM_Expert_{index}")(inputs)
        experts.append(Flatten(name=f"Flatten_Expert_{index}")(sequence))
    gate = Dense(3, activation="softmax", name="Gating_Network")(inputs[:, -1, :])
    # Stack experts on a new axis so the 3 gate weights can scale them.
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

