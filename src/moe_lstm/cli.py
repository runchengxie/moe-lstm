"""Command-line study run."""

import os

import pandas as pd
from sklearn.metrics import confusion_matrix

from moe_lstm.constants import LOOKBACK, MANUAL_FEATURE_COLUMNS, METRIC_COLUMNS, N_CLUSTERS, THRESHOLD
from moe_lstm.data import (
    build_feature_frame,
    cluster_matrix,
    load_study_prices,
    prediction_rows,
    select_kmeans_features,
    select_som_features,
    session_gap_warning,
    window_split,
)
from moe_lstm.eval import backtest, buy_and_hold_equity, oos_probability_frame, write_oos_probabilities
from moe_lstm.train import resolve_epochs, train_and_predict_moe

_FIGURE_NAMES = {
    "Close Price over Time": "close.png",
    "Correlation Matrix of Selected Features": "correlation.png",
    "Cumulative Returns Comparison": "equity.png",
    "Daily Returns Comparison": "daily_returns.png",
}


def _figure_filename(figure, number: int) -> str:
    titles = [axis.get_title() or "" for axis in figure.axes]
    if any("Confusion Matrix" in title for title in titles):
        return "confusion.png"
    for title in titles:
        if title in _FIGURE_NAMES:
            return _FIGURE_NAMES[title]
    return f"figure_{number}.png"


def _show(plt) -> None:
    """Display figures on an interactive backend and stay quiet under Agg.

    ``MOE_RESULTS_DIR`` saves each open figure before the backend closes it.
    """
    import matplotlib

    results_dir = os.environ.get("MOE_RESULTS_DIR", "").strip()
    if results_dir:
        os.makedirs(results_dir, exist_ok=True)
        for number in plt.get_fignums():
            figure = plt.figure(number)
            figure.savefig(
                os.path.join(results_dir, _figure_filename(figure, number)),
                dpi=140,
                bbox_inches="tight",
                facecolor=figure.get_facecolor(),
            )
    if matplotlib.get_backend().lower() == "agg":
        plt.close("all")
        return
    plt.show()


def _write_result_tables(metrics: pd.DataFrame, results: list[dict], df_test: pd.DataFrame) -> None:
    """Write the printed metrics, equity curves, and uncosted buy and hold."""
    results_dir = os.environ.get("MOE_RESULTS_DIR", "").strip()
    if not results_dir:
        return
    os.makedirs(results_dir, exist_ok=True)
    metrics.to_csv(os.path.join(results_dir, "metrics.csv"), index=False)
    equity = pd.DataFrame({"Date": pd.Series(df_test["Date"]).reset_index(drop=True)})
    for result in results:
        equity[result["Model"]] = pd.Series(result["Cumulative"]).reset_index(drop=True).to_numpy()
    equity["Buy & Hold"] = buy_and_hold_equity(df_test["Tomorrow_Change"]).reset_index(drop=True).to_numpy()
    equity.to_csv(os.path.join(results_dir, "equity.csv"), index=False)
    held = backtest([1] * len(df_test), df_test, "Buy & Hold", fee=0.0)
    pd.DataFrame(
        [
            {
                "Model": "Buy & Hold",
                "Total Return": held["Total Return"],
                "Max Drawdown": held["Max Drawdown"],
                "Sharpe Ratio": held["Sharpe Ratio"],
            }
        ]
    ).to_csv(os.path.join(results_dir, "buy_and_hold.csv"), index=False)


def _print_overview(frame: pd.DataFrame) -> None:
    print("===== 数据前几行 =====")
    print(frame.head())
    print("\n===== 数据信息 =====")
    print(frame.info())
    print("\n===== 描述统计 =====")
    print(frame.describe())
    print("\n===== 缺失值统计 =====")
    print(frame.isnull().sum())


def _plot_close(frame: pd.DataFrame) -> None:
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.plot(frame["Date"], frame["Close/Last"], label="Close Price")
    axis = plt.gca()
    axis.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.title("Close Price over Time")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.setp(axis.xaxis.get_majorticklabels(), rotation=45)
    _show(plt)


def _plot_correlation(frame: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Descriptive only. Feature selection uses the fit rows, not this matrix.
    correlation = frame[list(MANUAL_FEATURE_COLUMNS)].corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap="coolwarm")
    plt.title("Correlation Matrix of Selected Features")
    _show(plt)


def _plot_results(results: list[dict], df_test: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(figsize=(15, 4))
    for index, result in enumerate(results):
        plt.subplot(1, len(results), index + 1)
        matrix = confusion_matrix(result["y_test"], result["predictions"], labels=[0, 1])
        sns.heatmap(
            matrix,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=["Not above", "Above"],
            yticklabels=["Not above", "Above"],
        )
        plt.title(f"{result['Model']} Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("True")
    plt.tight_layout()
    _show(plt)

    plt.figure(figsize=(14, 7))
    for result in results:
        plt.plot(df_test["Date"], result["Cumulative"], label=result["Model"])
    plt.plot(
        df_test["Date"],
        buy_and_hold_equity(df_test["Tomorrow_Change"]),
        label="Buy & Hold",
        linestyle="--",
    )
    plt.title("Cumulative Returns Comparison")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.legend()
    plt.xticks(rotation=45)
    _show(plt)

    # Percent change of each equity curve, including the first NaN point.
    plt.figure(figsize=(14, 5))
    for result in results:
        plt.plot(df_test["Date"], result["Cumulative"].pct_change(), label=result["Model"])
    plt.title("Daily Returns Comparison")
    plt.xlabel("Date")
    plt.ylabel("Daily Return")
    plt.legend()
    _show(plt)


def _metrics_table(results: list[dict]) -> pd.DataFrame:
    return pd.DataFrame([{column: result[column] for column in METRIC_COLUMNS} for result in results])


def main(epochs: int | None = None) -> pd.DataFrame:
    epochs = resolve_epochs(epochs)
    raw = load_study_prices()
    _print_overview(raw)
    _plot_close(raw)

    try:
        frame = build_feature_frame(raw, THRESHOLD)
        split = window_split(len(frame), LOOKBACK)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    warning = session_gap_warning(frame["Date"])
    if warning:
        print(warning)

    print(frame[["Date", "Close/Last", "Daily_Return", "Tomorrow_Change", "Target"]].head(10))
    balance_counts = frame["Target"].value_counts()
    print("标签分布：")
    print(balance_counts)
    print("\n占比：")
    print(balance_counts / len(frame))
    _plot_correlation(frame)

    manual = list(MANUAL_FEATURE_COLUMNS)
    clustered = cluster_matrix(frame.loc[:, manual].to_numpy(dtype=float), split.n_scale_rows)
    kmeans_columns = select_kmeans_features(clustered, manual, N_CLUSTERS)
    som_columns = select_som_features(clustered, manual)
    print("K-Means Selected Features:", kmeans_columns)
    print("SOM Selected Features:", som_columns)

    df_test = prediction_rows(frame, LOOKBACK, split.n_test)
    results = []
    for feature_columns, model_name in zip(
        (manual, kmeans_columns, som_columns),
        ("Manual", "KMeans", "SOM"),
    ):
        model_result = train_and_predict_moe(
            frame,
            feature_columns,
            model_name,
            LOOKBACK,
            epochs=epochs,
        )
        if len(model_result["predictions"]) != len(df_test):
            raise RuntimeError("Test prediction length does not match the backtest rows.")
        backtest_result = backtest(model_result["predictions"], df_test, model_name)
        results.append(
            {
                "Model": model_name,
                "y_test": model_result["y_test"],
                "predictions": model_result["predictions"],
                "probabilities": model_result["probabilities"],
                "Accuracy": model_result["accuracy"],
                "Precision": model_result["precision"],
                "Recall": model_result["recall"],
                "F1": model_result["f1"],
                "AUC-ROC": model_result["auc_roc"],
                "Total Return": backtest_result["Total Return"],
                "Max Drawdown": backtest_result["Max Drawdown"],
                "Sharpe Ratio": backtest_result["Sharpe Ratio"],
                "Cumulative": backtest_result["Cumulative"],
            }
        )

    oos_path = os.environ.get("MOE_OOS_CSV", "oos_probabilities.csv")
    write_oos_probabilities(
        [
            oos_probability_frame(
                df_test["Date"],
                result["Model"],
                result["probabilities"],
                result["predictions"],
            )
            for result in results
        ],
        oos_path,
    )
    print(f"OOS probabilities written to {oos_path}")

    metrics = _metrics_table(results)
    print("\n===== 模型性能对比 =====")
    print(metrics.round(3))
    _plot_results(results, df_test)
    _write_result_tables(metrics, results, df_test)
    print(metrics[["Model", "Total Return", "Max Drawdown", "Sharpe Ratio"]])
    return metrics


def cli() -> None:
    """Console-script entry. ``main`` still returns the metrics frame."""
    main()

