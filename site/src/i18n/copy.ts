export type Locale = "zh" | "en";

export type Localized = Record<Locale, string>;

export const locales: Locale[] = ["zh", "en"];

export const L = (zh: string, en: string): Localized => ({ zh, en });

export const links = {
  repo: "https://github.com/runchengxie/moe_lstm",
  pr1: "https://github.com/runchengxie/moe_lstm/pull/1",
  pr2: "https://github.com/runchengxie/moe_lstm/pull/2",
  pr3: "https://github.com/runchengxie/moe_lstm/pull/3",
  pr4: "https://github.com/runchengxie/moe_lstm/pull/4",
  pr5: "https://github.com/runchengxie/moe_lstm/pull/5",
  pr6: "https://github.com/runchengxie/moe_lstm/pull/6",
  pr7: "https://github.com/runchengxie/moe_lstm/pull/7",
  engine: "https://github.com/runchengxie/quant-backtest-engine",
  pages: "https://runchengxie.github.io/moe_lstm/",
  defaultCsv:
    "https://raw.githubusercontent.com/runchengxie/quant_practice_3/refs/heads/main/historical_data.csv",
} as const;

export const ui = {
  skip: L("跳到正文", "Skip to content"),
  langLabel: L("语言", "Language"),
  themeLabel: L("颜色", "Theme"),
  langZh: L("中文", "中文"),
  langEn: L("EN", "EN"),
  themeLight: L("浅色", "Light"),
  themeDark: L("深色", "Dark"),
  themeSystem: L("系统", "System"),
  navLabel: L("站点", "Site"),
  navHome: L("首页", "Home"),
  navDocs: L("文档", "Docs"),
  navChangelog: L("变更", "Changelog"),
  footer: L(
    "研究脚本，不提供交易信号。仓库和本站都不放行情。",
    "A research script, with no trading signals. The repository and this site do not host market data.",
  ),
};

const merged = L("已合并", "Merged");

export const copy = {
  meta: {
    title: L("moe_lstm · 回测与结构", "moe_lstm · results and architecture"),
    description: L(
      "MoE-LSTM 的回测位置还是占位，结构说明包括专家、门控、Hive Parquet 与 CSV 回退。研究脚本，不是交易系统。",
      "Placeholder backtest slots for an MoE-LSTM, plus how the experts, gate, Hive Parquet path, and CSV fallback fit together. A research script, not a trading system.",
    ),
  },
  hero: {
    kicker: L("研究脚本", "Research script"),
    title: L("下一交易日涨跌的 MoE-LSTM", "An MoE-LSTM for the next session"),
    lede: L(
      "三个 LSTM 专家加一个门控。首页先留出回测结果的位置，再说明数据怎么进来、窗口怎么切。",
      "Three LSTM experts and a gate. The home page reserves a place for backtest results, then how data comes in and how the windows are split.",
    ),
    notices: [
      {
        tone: "limit" as const,
        text: L("研究脚本，不是交易系统。", "Research script, not a trading system."),
      },
      {
        tone: "limit" as const,
        text: L("仓库和本站都没有行情数据。", "No market data in the repository or on this site."),
      },
    ],
    asOf: L(
      "写于 2026-11-05（Asia/Shanghai），对应 main 的 `37671ab`（#7 的 squash）。#1、#2、#3、#4、#6、#7 已合并。远程只有 `main`。#5 已关闭，没有合并。",
      "Written 2026-11-05 (Asia/Shanghai), against main at `37671ab` (the squash of #7). #1, #2, #3, #4, #6, and #7 are merged. The only remote branch is `main`. #5 was closed and was not merged.",
    ),
  },
  what: {
    index: "01",
    heading: L("是什么", "What it is"),
    facts: [
      {
        term: L("标的", "Subject"),
        detail: L(
          "脚本注释里的问题陈述是标普 500、日频、下一交易日涨跌，并写了 2020-01-13 至 2025-01-10。这段行情不在仓库里。",
          "The script's problem statement says S&P 500, daily bars, and next-session up or down, and it names the window 13 Jan 2020–10 Jan 2025. That history is not in the repository.",
        ),
      },
      {
        term: L("标签", "Label"),
        detail: L(
          "下一根 K 线的收盘到收盘收益高于 0.2%（`THRESHOLD = 0.002`）记为 1，否则为 0。回看 `LOOKBACK = 5`。",
          "The next bar is 1 when its close-to-close return is above 0.2% (`THRESHOLD = 0.002`); otherwise it is 0. Lookback is `LOOKBACK = 5`.",
        ),
      },
      {
        term: L("模型", "Model"),
        detail: L(
          "三个 LSTM（各 64 单元，保留时间维）展平后堆在一起。门控是宽度为 3 的 softmax，只看输入的最后一根。加权求和后接 sigmoid，概率大于 0.5 判为涨。损失是 binary crossentropy，优化器是 Adam。",
          "Three LSTMs (64 units, sequences kept) are flattened and stacked. The gate is a width-3 softmax on the last input bar only. A weighted sum feeds a sigmoid; a probability above 0.5 is up. Loss is binary crossentropy. The optimizer is Adam.",
        ),
      },
      {
        term: L("划分", "Split"),
        detail: L(
          "按时间取前 80% 的窗口训练、后 20% 测试，最多 50 个 epoch，batch 16，早停 patience 5。训练段的最后 20% 是早停验证集，至少留一个验证窗口。`MinMaxScaler` 只在拟合窗口的特征行上拟合。这是已合并的 #3 留在 main 上的行为。",
          "The first 80% of windows train and the last 20% test, for up to 50 epochs, batch size 16, and early-stopping patience 5. The last 20% of the training block is the early-stopping validation set, with at least one validation window. `MinMaxScaler` is fit only on the feature rows of the fit windows. That is what merged #3 left on main.",
        ),
      },
      {
        term: L("运行时", "Runtime"),
        detail: L(
          "根 README 写明在 Python 3.12 上核对过。安装用 uv 0.13.7：`uv sync` 读取 `pyproject.toml` 和 `uv.lock`。直接依赖钉到 TensorFlow 2.21.0、Keras 3.15.1、pandas 3.1.1、numpy 2.5.4、scikit-learn 1.9.1、MiniSom 2.3.6、matplotlib 3.11.2、seaborn 0.13.2、pyarrow 26.0.1。`requirements.txt` 已随 #6 删除。smoke 和 unittest 的 CI 使用 `uv sync --frozen`。",
          "The root README records a check on Python 3.12. Install with uv 0.13.7: `uv sync` reads `pyproject.toml` and `uv.lock`. Direct pins are TensorFlow 2.21.0, Keras 3.15.1, pandas 3.1.1, numpy 2.5.4, scikit-learn 1.9.1, MiniSom 2.3.6, matplotlib 3.11.2, seaborn 0.13.2, and pyarrow 26.0.1. `requirements.txt` was removed in #6. Smoke and unit CI run `uv sync --frozen`.",
        ),
      },
    ],
  },
  arch: [
    { n: "1", k: L("输入", "Input"), v: L("5 根 × 选定列", "5 bars × selected columns") },
    { n: "2", k: L("专家", "Experts"), v: L("LSTM × 3，各 64", "LSTM × 3, 64 each") },
    { n: "3", k: L("门控", "Gate"), v: L("softmax × 3", "softmax × 3") },
    { n: "4", k: L("输出", "Output"), v: L("sigmoid，阈值 0.5", "sigmoid, cutoff 0.5") },
  ],
  pipeline: {
    index: "02",
    heading: L("流程", "Pipeline"),
    steps: [
      {
        name: L("OHLCV", "OHLCV"),
        detail: L(
          "设置了 `MOE_DATA_PARQUET` 时读取 Hive 分钟 Parquet，并聚合成日线；还要设置 `MOE_SYMBOL`。未设置时从 `MOE_DATA_CSV` 读入 `Date`、`Open`、`High`、`Low`、`Close/Last`。CSV 也未设置时用脚本里的默认 URL；该 URL 在 2026-11-05 返回 HTTP 404。",
          "When `MOE_DATA_PARQUET` is set, the script reads Hive minute Parquet and rolls it up to daily bars, and `MOE_SYMBOL` is required. Otherwise it reads `Date`, `Open`, `High`, `Low`, and `Close/Last` from `MOE_DATA_CSV`. If that is also unset, it uses the default URL in the file. That URL returned HTTP 404 on 2026-11-05.",
        ),
      },
      {
        name: L("特征", "Features"),
        detail: L(
          "由 `Close/Last` 计算 MA5、MA10、EMA5、EMA10、14 日 RSI、20 日布林带、MACD(12, 26, 9)、日收益和 10 日波动，并带上 Open、High、Low。",
          "From `Close/Last`: MA5, MA10, EMA5, EMA10, 14-day RSI, 20-day Bollinger bands, MACD (12, 26, 9), daily return, and 10-day volatility, plus Open, High, and Low.",
        ),
      },
      {
        name: L("子集", "Subsets"),
        detail: L(
          "手工列是上面的全集。K-Means 把每一列当成一个样本，分成 5 簇，每簇留离中心最近的一列。SOM 是 3×3 网格，每个被占用的格子留最近的一列。",
          "The manual set is that full list. K-Means treats each column as a sample, uses 5 clusters, and keeps the column closest to each center. The SOM is a 3×3 grid and keeps the closest column in each occupied cell.",
        ),
      },
      {
        name: L("MoE", "MoE"),
        detail: L(
          "Manual、KMeans、SOM 三个子集各训练一次同一个结构：三个 LSTM 专家加门控。",
          "Manual, KMeans, and SOM each train the same architecture once: three LSTM experts and a gate.",
        ),
      },
      {
        name: L("回测", "Backtest"),
        detail: L(
          "测试段上，预测为 1 则做多，为 0 则做空，并与买入持有对照。脚本打印 accuracy、precision、recall、F1、AUC-ROC、总收益、最大回撤，以及按 √252 年化的夏普。本页不记录任何一次运行的数值。",
          "On the test slice, a prediction of 1 is long and a prediction of 0 is short, compared with buy and hold. The script prints accuracy, precision, recall, F1, AUC-ROC, total return, max drawdown, and a Sharpe ratio annualized with √252. This page does not record figures from any run.",
        ),
      },
    ],
    note: L(
      "一次运行训练三个模型：手工特征、K-Means 子集、SOM 子集。相关热力图只供查看，仍使用全样本。`MPLBACKEND=Agg` 时画出图后关闭，不调用 `plt.show()`。交互式后端仍会调用 `plt.show()`。",
      "One run fits three models: manual features, the K-Means subset, and the SOM subset. The correlation heatmap is for inspection and still uses the full sample. With `MPLBACKEND=Agg` the script draws the figures and closes them, and does not call `plt.show()`. An interactive backend still calls `plt.show()`.",
    ),
  },
  data: {
    index: "03",
    heading: L("数据", "Data"),
    intro: L(
      "行情放在仓库外面。主路径是 Hive 分钟 Parquet；未设置时回退到 CSV。价格列要已经是数字：美元符号或千分位会让滚动计算失败。",
      "Keep prices outside the repository. Hive minute Parquet is the primary path; CSV is the fallback when that root is unset. Price columns must already be numbers. A dollar sign or thousands separator breaks the rolling calculations.",
    ),
    env: [
      {
        name: "MOE_DATA_PARQUET",
        detail: L(
          "已在 main（#4）。Hive 分钟 Parquet 根目录。需要同时设置 `MOE_SYMBOL`；一个代码有多份 security 时再设置 `MOE_SECURITY`。设置之后优先于 `MOE_DATA_CSV`。分钟线聚合成脚本已有的日线列。不设置时仍走 CSV。",
          "On main since #4. Hive minute-Parquet root. Set `MOE_SYMBOL` with it, and `MOE_SECURITY` when one ticker has more than one security hash. When set, it wins over `MOE_DATA_CSV`. Minutes are rolled up to the daily columns the script already uses. Unset, the script still reads CSV.",
        ),
      },
      {
        name: "MOE_DATA_CSV",
        detail: L(
          "Parquet 根目录未设置时的日频 CSV，可以是本地路径或 `pandas.read_csv` 能打开的 URL。这一项和 Parquet 都未设置时，脚本请求下面的默认 URL。撰写 README 时该 URL 返回 HTTP 404（`quant_practice_3` 已不在）。",
          "Daily CSV used when the Parquet root is unset. A local path or any URL `pandas.read_csv` can open. If this and the Parquet root are both unset, the script requests the default URL below. When the README was written that URL returned HTTP 404 (`quant_practice_3` is gone).",
        ),
      },
    ],
    columns: [
      {
        name: "Date",
        rule: L(
          "CSV 只用 `%m/%d/%Y`，例如 `01/13/2020`。ISO 日期会解析失败。",
          "CSV dates are parsed only as `%m/%d/%Y`, for example `01/13/2020`. ISO dates fail to parse.",
        ),
      },
      {
        name: "Close/Last",
        rule: L(
          "收盘价，数字。指标、标签和回测都用这一列。",
          "Numeric close. Indicators, the label, and the backtest all use this column.",
        ),
      },
      {
        name: "Open",
        rule: L("开盘价，数字。", "Numeric open."),
      },
      {
        name: "High",
        rule: L("最高价，数字。", "Numeric high."),
      },
      {
        name: "Low",
        rule: L("最低价，数字。", "Numeric low."),
      },
    ],
    columnCaption: L("CSV 列", "CSV columns"),
    parquetRun: L("Hive 分钟线", "Hive minute bars"),
    csvRun: L("CSV 回退", "CSV fallback"),
    runNote: L(
      "`uv sync` 按 `pyproject.toml` 和 `uv.lock` 安装。smoke 和 unittest 的 CI 使用 `uv sync --frozen`。仓库里没有 `requirements.txt`。更完整的安装说明在 `docs/setup.zh-CN.md`。",
      "`uv sync` installs from `pyproject.toml` and `uv.lock`. Smoke and unit CI use `uv sync --frozen`. There is no `requirements.txt`. The longer setup note is in `docs/setup.md`.",
    ),
    vendor: L(
      "`docs/data.zh-CN.md` 说明 AlgoSeek 的美股 bar 不是上面的 CSV 列名，要在单独的文件里映射成这五列。Hive 分钟 Parquet 是另一条已在 main 上的路径：加载器按分钟字段聚合成这些日线列。未设置 Parquet 根目录时才走 CSV。",
      "`docs/data.md` states that AlgoSeek US equity bars are not the CSV schema above. Map them onto these five columns in a separate file. Hive minute Parquet is a separate path already on main: the loader rolls minute fields up to these daily columns. CSV is used only when the Parquet root is unset.",
    ),
    defaultUrl: L(
      "默认 CSV URL，撰写 README 时返回 HTTP 404：",
      "Default CSV URL, HTTP 404 when the README was written:",
    ),
  },
  merged: {
    index: "04",
    heading: L("已在 main", "On main"),
    intro: L(
      "按编号列出。已合并的都是 squash 进 main。远程分支只有 `main`。这批没有仍开着的 pull request。标题是 GitHub 上的英文原题。",
      "Listed by number. Merged items were squash-merged into main. The only remote branch is `main`. No pull request from this batch is still open. Titles are the English titles on GitHub.",
    ),
    items: [
      {
        n: "#1",
        href: links.pr1,
        title: "Fix fresh-run blockers in the MoE-LSTM script",
        state: merged,
        base: L("squash `0309d55`", "squash `0309d55`"),
        body: L(
          "运维健康：让本地 CSV 能够启动训练。",
          "Ops health: a local CSV can start training.",
        ),
      },
      {
        n: "#2",
        href: links.pr2,
        title: "Pin dependency versions and add a one-epoch CI smoke",
        state: merged,
        base: L("squash `0acab47`", "squash `0acab47`"),
        body: L(
          "钉住直接依赖，并加上一轮 epoch 的 smoke，夹具是合成 K 线。这些钉版本现由 #6 放在 `pyproject.toml` 与 `uv.lock`，并包含 pyarrow。",
          "Pins the direct dependencies and adds a one-epoch smoke on a synthetic bar fixture. Those pins now live in `pyproject.toml` and `uv.lock` via #6, and include pyarrow.",
        ),
      },
      {
        n: "#3",
        href: links.pr3,
        title: "Fix backtest alignment, leakage, and sync the docs",
        state: merged,
        base: L("squash `2b56c06`", "squash `2b56c06`"),
        body: L(
          "修正回测对齐和信息泄漏，补上测试，并让中英文说明与代码一致。上文的切分和缩放就是这份改动。准确的双语文档也是从这里进 main 的。",
          "Corrects backtest alignment and leakage, adds tests, and syncs the Chinese and English docs to the code. The split and scaling above are this change. The accurate bilingual docs entered main here.",
        ),
      },
      {
        n: "#4",
        href: links.pr4,
        title: "Load daily bars from Hive minute Parquet",
        state: merged,
        base: L("squash `d47ba61`", "squash `d47ba61`"),
        body: L(
          "读取 Hive 分钟 Parquet（`MOE_DATA_PARQUET`、`MOE_SYMBOL`，必要时 `MOE_SECURITY`）并聚合成日线。CSV 仍是回退。",
          "Reads Hive minute Parquet (`MOE_DATA_PARQUET`, `MOE_SYMBOL`, and `MOE_SECURITY` when needed) and aggregates it to daily bars. CSV remains the fallback.",
        ),
      },
      {
        n: "#5",
        href: links.pr5,
        title: "Add Simplified Chinese README (README.zh-CN.md)",
        state: L("已关闭", "Closed"),
        base: L("未合并", "Not merged"),
        body: L(
          "已关闭，视为被取代。准确的中英文档随 #3 进入 main。根 README 顶部的语言切换随 #6 进入 main。",
          "Closed as superseded. The accurate bilingual docs landed with #3. The language switcher on the root READMEs landed with #6.",
        ),
      },
      {
        n: "#6",
        href: links.pr6,
        title: "Switch dependency management from pip to uv",
        state: merged,
        base: L("squash `7b8f839`", "squash `7b8f839`"),
        body: L(
          "安装从 pip 换成 uv：`pyproject.toml` 加 `uv.lock`，`requirements.txt` 删除。运行是 `uv sync` 和 `uv run python moe_lstm.py`。smoke 与 unittest 的 CI 使用 `uv sync --frozen`。根 README 的语言切换也在这份里。",
          "Switches installs from pip to uv: `pyproject.toml` plus `uv.lock`, and `requirements.txt` removed. Run with `uv sync` and `uv run python moe_lstm.py`. Smoke and unit CI use `uv sync --frozen`. The language switcher on the root READMEs is in this change.",
        ),
      },
      {
        n: "#7",
        href: links.pr7,
        title: "Add a bilingual Astro brief and GitHub Pages deploy",
        state: merged,
        base: L("squash `37671ab`", "squash `37671ab`"),
        body: L(
          "`site/` 下的这份 Astro 简报，以及 GitHub Pages 工作流。地址就是本页。",
          "This Astro brief under `site/`, and the GitHub Pages workflow. This page is that site.",
        ),
      },
    ],
    note: L(
      "还没做的只有下一节的两件事。",
      "The only work still planned is the two items in the next section.",
    ),
  },
  next: {
    index: "05",
    heading: L("还没做", "Not done yet"),
    intro: L("这两件不在 main 上。", "These two are not on main."),
    items: [
      {
        term: L("`src/moe_lstm/`", "`src/moe_lstm/`"),
        detail: L(
          "把根目录脚本拆成这个包。还没有做。",
          "Split the root script into this package. Not done.",
        ),
      },
      {
        term: L("quant-backtest-engine", "quant-backtest-engine"),
        detail: L(
          "模型只输出信号或权重。成交和账本由这个库负责。还没有接上。",
          "The model would emit signals or weights. Fills and the ledger would belong to this library. Not wired up.",
        ),
        href: links.engine,
      },
    ],
  },
  links: {
    index: "06",
    heading: L("链接", "Links"),
    items: [
      {
        href: links.repo,
        label: L("runchengxie/moe_lstm", "runchengxie/moe_lstm"),
        note: L(
          "本仓库。脚本、`pyproject.toml`、`uv.lock` 和运行说明。",
          "This repository. Script, `pyproject.toml`, `uv.lock`, and how to run it.",
        ),
      },
      {
        href: links.engine,
        label: L("quant-backtest-engine", "quant-backtest-engine"),
        note: L(
          "计划中的回测库，还没有接上。模型将输出信号或权重，由它处理成交和账本。本仓库的依赖在 `pyproject.toml` 和 `uv.lock`。",
          "The planned backtest library. It is not wired up. The model would emit signals or weights; it would handle fills and the ledger. This repository's dependencies are in `pyproject.toml` and `uv.lock`.",
        ),
      },
      {
        href: links.pages,
        label: L("GitHub Pages", "GitHub Pages"),
        note: L(
          "本页。站点和工作流已随 #7 进入 main。",
          "This page. The site and the workflow landed on main with #7.",
        ),
      },
    ],
  },
  missing: {
    title: L("没有这一页", "No such page"),
    body: L("这一页不在简报或文档里。", "This page is not in the brief or the docs."),
    home: L("回到首页", "Back home"),
  },
};

export const showcase = {
  kicker: L("结果", "Results"),
  heading: L("回测展示", "Performance"),
  empty: L(
    "这些格子是占位，不是结果。这里没有存任何一次运行。数字等 quant-backtest-engine 接上之后才会放进来。本页不编造收益、夏普或任何数值。",
    "These cells are placeholders, not results. No run is stored here. Figures are coming once quant-backtest-engine is wired. This page does not invent returns, Sharpe ratios, or any other number.",
  ),
  chartTitle: L("权益曲线", "Equity"),
  chartEmpty: L("占位，没有曲线", "Placeholder, no series"),
  axisY: L("权益", "Equity"),
  axisX: L("测试窗口", "Test windows"),
  tableCaption: L("脚本会打印的列。格子仍是空的。", "Columns the script prints. The cells are still empty."),
  modelHeading: L("模型", "Model"),
  models: [
    { id: "manual", name: "Manual" },
    { id: "kmeans", name: "KMeans" },
    { id: "som", name: "SOM" },
    { id: "buy-hold", name: "Buy & hold" },
  ],
  columns: [
    { key: "accuracy", label: "Accuracy" },
    { key: "precision", label: "Precision" },
    { key: "recall", label: "Recall" },
    { key: "f1", label: "F1" },
    { key: "auc-roc", label: "AUC-ROC" },
    { key: "total-return", label: "Total Return" },
    { key: "max-drawdown", label: "Max Drawdown" },
    { key: "sharpe", label: "Sharpe Ratio" },
  ],
  emptyMark: "—",
  definitions: L("指标怎么定义，写在训练文档里。", "How the metrics are defined is in the training note."),
};

export const architecture = {
  kicker: L("结构", "Architecture"),
  heading: L("模型怎么接在一起", "How the model is put together"),
  lede: L(
    "三个 LSTM 专家读同一段窗口，门控只看最后一根。数据以 Hive 分钟 Parquet 为主，CSV 是回退。",
    "Three LSTM experts read the same window, and the gate sees only the last bar. Hive minute Parquet is the primary input. CSV is the fallback.",
  ),
  dataHeading: L("数据路径", "Data path"),
  data: L(
    "设置 `MOE_DATA_PARQUET` 时，Hive 分钟线是主输入，并要有 `MOE_SYMBOL`；同一代码有多份 security 时再设 `MOE_SECURITY`。分钟线收成日线。未设置 Parquet 根目录时回退到 `MOE_DATA_CSV`。仓库里没有行情。脚本自带的远程 CSV 在 2026-11-05 返回 HTTP 404，所以 CSV 需要本地路径。",
    "When `MOE_DATA_PARQUET` is set, Hive minute bars are the primary input, together with `MOE_SYMBOL`, and `MOE_SECURITY` when one ticker has more than one security hash. Minutes roll up to daily bars. `MOE_DATA_CSV` is the fallback when that Parquet root is unset. The repository has no market data. The default remote CSV returned HTTP 404 on 2026-11-05, so a CSV run needs a local path.",
  ),
  splitHeading: L("窗口、切分和缩放", "Windows, split, and scaling"),
  split: L(
    "回看 `LOOKBACK = 5`。按时间，前 80% 的窗口训练，后 20% 测试。训练段最后 20% 做早停验证。`MinMaxScaler` 只在拟合窗口的特征行上拟合。标签：下一根收盘到收盘收益高于 0.2%（`THRESHOLD = 0.002`）为 1，等于 0.2% 为 0。最多 50 个 epoch，batch 16，早停 patience 5。手工特征、K-Means（5 簇）、3×3 SOM 三个子集各训练一次同一结构。预测 1 做多，0 做空，对照买入持有。",
    "Lookback is `LOOKBACK = 5`. In time order, the first 80% of windows train and the last 20% test. The last 20% of the training block is the early-stopping validation set. `MinMaxScaler` is fit only on the feature rows of the fit windows. The label is 1 when the next close-to-close return is above 0.2% (`THRESHOLD = 0.002`), and 0 when it is equal to 0.2%. Up to 50 epochs, batch size 16, early-stopping patience 5. Manual features, K-Means (5 clusters), and a 3×3 SOM each train that same architecture once. A prediction of 1 is long and 0 is short, set against buy and hold.",
  ),
  more: L("列约定、费用和打印的指标在文档里。", "Column rules, fees, and the printed metrics are in the docs."),
};

export const changelogCopy = {
  title: L("变更", "Changelog"),
  lede: L(
    "合并顺序放在这里，不放在首页。",
    "The merge list lives here, not on the home page.",
  ),
};

export const parquetCommand = `uv sync
export MOE_DATA_PARQUET=/path/to/dataset-root
export MOE_SYMBOL=AAPL
export MPLBACKEND=Agg
uv run python moe_lstm.py`;

export const csvCommand = `export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
uv run python moe_lstm.py`;
