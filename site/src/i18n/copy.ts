export type Locale = "zh" | "en";

export type Localized = Record<Locale, string>;

export const locales: Locale[] = ["zh", "en"];

export const L = (zh: string, en: string): Localized => ({ zh, en });

export const links = {
  repo: "https://github.com/runchengxie/moe-lstm",
  pr1: "https://github.com/runchengxie/moe-lstm/pull/1",
  pr2: "https://github.com/runchengxie/moe-lstm/pull/2",
  pr3: "https://github.com/runchengxie/moe-lstm/pull/3",
  pr4: "https://github.com/runchengxie/moe-lstm/pull/4",
  pr5: "https://github.com/runchengxie/moe-lstm/pull/5",
  pr6: "https://github.com/runchengxie/moe-lstm/pull/6",
  pr7: "https://github.com/runchengxie/moe-lstm/pull/7",
  engine: "https://github.com/runchengxie/quant-backtest-engine",
  pages: "https://runchengxie.github.io/moe-lstm/",
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
    "脚本在终端打印指标。行情文件留在仓库外面。",
    "The script prints metrics in the terminal. Price files stay outside the repository.",
  ),
};

const merged = L("已合并", "Merged");

export const copy = {
  meta: {
    title: L("moe_lstm 回测和结构", "moe_lstm results and architecture"),
    description: L(
      "回测格子空着。页面写下三个 LSTM 专家、门控、Hive Parquet，以及 CSV 回退。",
      "The backtest cells are empty. The page describes three LSTM experts, the gate, Hive Parquet, and the CSV fallback.",
    ),
  },
  hero: {
    kicker: L("研究脚本", "Research script"),
    title: L("下一交易日收益的 MoE-LSTM", "An MoE-LSTM for the next session's return"),
    lede: L(
      "三个 LSTM 专家读同一段窗口。门控读最后一根。回测格子空着。",
      "Three LSTM experts read one window. The gate reads the last bar. The backtest cells are empty.",
    ),
    notices: [
      {
        tone: "limit" as const,
        text: L("脚本在终端打印指标。", "The script prints metrics in the terminal."),
      },
      {
        tone: "limit" as const,
        text: L("行情文件留在仓库外面。", "Price files stay outside the repository."),
      },
    ],
    asOf: L(
      "页面写于 2026-11-05（Asia/Shanghai），对着 main 的 `37671ab`，也就是 #7 的 squash。#1、#2、#3、#4、#6、#7 已合并。远程分支是 `main`。#5 已关闭，没有并进 main。",
      "The page was written on 2026-11-05 (Asia/Shanghai), against main at `37671ab`, the squash of #7. #1, #2, #3, #4, #6, and #7 are merged. The remote branch is `main`. #5 was closed and did not merge.",
    ),
  },
  what: {
    index: "01",
    heading: L("是什么", "What it is"),
    facts: [
      {
        term: L("标的", "Subject"),
        detail: L(
          "脚本注释写的是标普 500，日频，下一交易日涨跌，区间 2020-01-13 至 2025-01-10。仓库里没有这段行情。",
          "The script comment names the S&P 500, daily bars, and next-session direction, for 2020-01-13 through 2025-01-10. That history is outside the repository.",
        ),
      },
      {
        term: L("标签", "Label"),
        detail: L(
          "下一根收盘到收盘的收益高于 0.2%（`THRESHOLD = 0.002`）时，标签记 1。其余记 0。回看是 `LOOKBACK = 5`。",
          "The label is 1 when the next close-to-close return is above 0.2% (`THRESHOLD = 0.002`). Every other return is 0. Lookback is `LOOKBACK = 5`.",
        ),
      },
      {
        term: L("模型", "Model"),
        detail: L(
          "三个 LSTM 各 64 单元，保留时间维，展平后堆在一起。门控是宽度 3 的 softmax，读最后一根。加权求和后接 sigmoid。概率大于 0.5 记为 1。损失是 binary crossentropy。优化器是 Adam。",
          "Three LSTMs, 64 units each, keep the time axis, then flatten and stack. The gate is a width-3 softmax and reads the last bar. A weighted sum goes into a sigmoid. A probability above 0.5 is class 1. The loss is binary crossentropy. The optimizer is Adam.",
        ),
      },
      {
        term: L("划分", "Split"),
        detail: L(
          "窗口按时间排。前 80% 训练，后 20% 测试。最多 50 个 epoch，batch 16，早停 patience 5。训练段最后 20% 做早停验证，至少留一个验证窗口。`MinMaxScaler` 只在拟合窗口的特征行上拟合。#3 合并之后，main 上就是这样切的。",
          "Windows stay in time order. The first 80% train. The last 20% test. Training runs up to 50 epochs, batch size 16, early-stopping patience 5. The last 20% of the training block is the early-stopping check, and at least one validation window stays. `MinMaxScaler` fits only the feature rows of the fit windows. After #3 merged, main splits the sample this way.",
        ),
      },
      {
        term: L("运行时", "Runtime"),
        detail: L(
          "根 README 记下一次核对，解释器是 Python 3.12。安装用 uv 0.13.7。`uv sync` 读 `pyproject.toml` 和 `uv.lock`。直接依赖钉在 TensorFlow 2.21.0、Keras 3.15.1、pandas 3.1.1、numpy 2.5.4、scikit-learn 1.9.1、MiniSom 2.3.6、matplotlib 3.11.2、seaborn 0.13.2、pyarrow 26.0.1。#6 删了 `requirements.txt`。smoke 和 unittest 的 CI 跑 `uv sync --frozen`。",
          "The root README records one check, on Python 3.12. Install with uv 0.13.7. `uv sync` reads `pyproject.toml` and `uv.lock`. The direct pins are TensorFlow 2.21.0, Keras 3.15.1, pandas 3.1.1, numpy 2.5.4, scikit-learn 1.9.1, MiniSom 2.3.6, matplotlib 3.11.2, seaborn 0.13.2, and pyarrow 26.0.1. #6 removed `requirements.txt`. Smoke and unit CI run `uv sync --frozen`.",
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
          "脚本读 Hive 分钟 Parquet，再收成日线。这时要设 `MOE_DATA_PARQUET` 和 `MOE_SYMBOL`。这两个空着时，脚本从 `MOE_DATA_CSV` 读 `Date`、`Open`、`High`、`Low`、`Close/Last`。CSV 也空着时，脚本去请求文件里的默认 URL。2026-11-05 那个 URL 返回 HTTP 404。",
          "The script reads Hive minute Parquet and rolls it up to daily bars. That path needs `MOE_DATA_PARQUET` and `MOE_SYMBOL`. When both are empty, the script reads `Date`, `Open`, `High`, `Low`, and `Close/Last` from `MOE_DATA_CSV`. When the CSV is empty too, the script requests the default URL in the file. On 2026-11-05 that URL returned HTTP 404.",
        ),
      },
      {
        name: L("特征", "Features"),
        detail: L(
          "脚本用 `Close/Last` 算 MA5、MA10、EMA5、EMA10、14 日 RSI、20 日布林带、MACD（12, 26, 9）、日收益和 10 日波动，再带上 Open、High、Low。",
          "From `Close/Last` the script builds MA5, MA10, EMA5, EMA10, 14-day RSI, 20-day Bollinger bands, MACD (12, 26, 9), daily return, and 10-day volatility, and it keeps Open, High, and Low.",
        ),
      },
      {
        name: L("子集", "Subsets"),
        detail: L(
          "手工列就是上面那张全表。K-Means 把每一列当成一个样本，分成 5 簇，每簇留下离中心最近的一列。SOM 用 3×3 网格，每个占住的格子留下最近的一列。",
          "The manual columns are that full list. K-Means treats each column as one sample, makes 5 clusters, and keeps the column closest to each center. The SOM uses a 3 by 3 grid and keeps the closest column in each occupied cell.",
        ),
      },
      {
        name: L("MoE", "MoE"),
        detail: L(
          "Manual、KMeans、SOM 三个子集各训练一次。结构相同，都是三个 LSTM 专家加一个门控。",
          "Manual, KMeans, and SOM each train once. The architecture is the same three LSTM experts and one gate.",
        ),
      },
      {
        name: L("回测", "Backtest"),
        detail: L(
          "测试段上，预测 1 做多，预测 0 空仓。类别 0 里有小涨，仓位记成空仓。旁边印着买入持有。脚本打印 accuracy、precision、recall、F1、AUC-ROC、总收益、最大回撤，还有按 √252 年化的夏普。这一页的格子空着。",
          "On the test slice, prediction 1 is long and prediction 0 is flat. Class 0 includes small gains, and the position stays flat. Buy and hold is printed beside it. The script prints accuracy, precision, recall, F1, AUC-ROC, total return, max drawdown, and a Sharpe ratio scaled by √252. The cells on this page are empty.",
        ),
      },
    ],
    note: L(
      "一次运行训练三个模型，手工特征、K-Means 子集、SOM 子集。相关热力图用全样本，给查看用。`MPLBACKEND=Agg` 时，脚本画完图就关掉，`plt.show()` 不调用。交互式后端会调用 `plt.show()`。",
      "One run trains three models, manual features, the K-Means subset, and the SOM subset. The correlation heatmap uses the full sample, for looking. With `MPLBACKEND=Agg` the script draws the figures and closes them. `plt.show()` stays uncalled. An interactive backend calls `plt.show()`.",
    ),
  },
  data: {
    index: "03",
    heading: L("数据", "Data"),
    intro: L(
      "行情文件留在仓库外面。主路径是 Hive 分钟 Parquet。根目录空着时，脚本读 CSV。价格列得已经是数字。美元符号或千分位会让滚动计算失败。",
      "Price files stay outside the repository. Hive minute Parquet is the primary path. When that root is empty, the script reads CSV. Price columns have to already be numbers. A dollar sign or a thousands separator breaks the rolling calculations.",
    ),
    env: [
      {
        name: "MOE_DATA_PARQUET",
        detail: L(
          "#4 合并后就在 main 上。这是 Hive 分钟 Parquet 的根目录。一起设 `MOE_SYMBOL`。一个代码有多份 security 时再设 `MOE_SECURITY`。设了之后盖过 `MOE_DATA_CSV`。分钟线收成脚本已经在用的日线列。根目录空着时，脚本读 CSV。",
          "This has been on main since #4. It is the Hive minute-Parquet root. Set `MOE_SYMBOL` with it. Set `MOE_SECURITY` when one ticker has more than one security hash. Once set, it wins over `MOE_DATA_CSV`. Minutes roll up to the daily columns the script already uses. When the root is empty, the script reads CSV.",
        ),
      },
      {
        name: "MOE_DATA_CSV",
        detail: L(
          "Parquet 根目录空着时，脚本读这份日频 CSV。路径可以在本地，也可以是 `pandas.read_csv` 打得开的 URL。这一项和 Parquet 都空着时，脚本请求下面的默认 URL。写 README 的时候，那个 URL 返回 HTTP 404。`quant_practice_3` 当时已经不在。",
          "When the Parquet root is empty, the script reads this daily CSV. The path can be local, or any URL `pandas.read_csv` can open. When this and the Parquet root are both empty, the script requests the default URL below. When the README was written, that URL returned HTTP 404. `quant_practice_3` was already gone.",
        ),
      },
    ],
    columns: [
      {
        name: "Date",
        rule: L(
          "CSV 只按 `%m/%d/%Y` 解析，例如 `01/13/2020`。ISO 日期解析失败。",
          "CSV dates parse only as `%m/%d/%Y`, for example `01/13/2020`. ISO dates fail to parse.",
        ),
      },
      {
        name: "Close/Last",
        rule: L(
          "收盘价，得是数字。指标、标签、回测都用这一列。",
          "The close, already a number. Indicators, the label, and the backtest use this column.",
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
      "`uv sync` 按 `pyproject.toml` 和 `uv.lock` 安装。smoke 和 unittest 的 CI 跑 `uv sync --frozen`。仓库里没有 `requirements.txt`。安装的长说明在 `docs/setup.zh-CN.md`。",
      "`uv sync` installs from `pyproject.toml` and `uv.lock`. Smoke and unit CI run `uv sync --frozen`. The repository has no `requirements.txt`. The longer setup note is `docs/setup.md`.",
    ),
    vendor: L(
      "`docs/data.zh-CN.md` 写着 AlgoSeek 美股 bar 用另一套列名。在单独的文件里映射成这五列。Hive 分钟 Parquet 是 main 上的另一条路径。加载器把分钟字段收成这些日线列。Parquet 根目录空着时，脚本读 CSV。",
      "`docs/data.md` says AlgoSeek US equity bars use other column names. Map them onto these five columns in a separate file. Hive minute Parquet is another path already on main. The loader rolls minute fields up to these daily columns. When the Parquet root is empty, the script reads CSV.",
    ),
    defaultUrl: L(
      "默认 CSV 地址在写 README 时返回 HTTP 404。",
      "The default CSV URL returned HTTP 404 when the README was written.",
    ),
  },
  merged: {
    index: "04",
    heading: L("已在 main", "On main"),
    intro: L(
      "下面按编号排。已合并的都是 squash 进 main。远程分支是 `main`。这批 pull request 都已经关上。标题用 GitHub 上的英文原题。",
      "The list is in number order. Merged items were squash-merged into main. The remote branch is `main`. Every pull request in this batch is closed. Titles are the English titles on GitHub.",
    ),
    items: [
      {
        n: "#1",
        href: links.pr1,
        title: "Fix fresh-run blockers in the MoE-LSTM script",
        state: merged,
        base: L("squash `0309d55`", "squash `0309d55`"),
        body: L(
          "本地 CSV 可以开始训练。",
          "A local CSV can start training.",
        ),
      },
      {
        n: "#2",
        href: links.pr2,
        title: "Pin dependency versions and add a one-epoch CI smoke",
        state: merged,
        base: L("squash `0acab47`", "squash `0acab47`"),
        body: L(
          "钉住直接依赖，加上一轮 epoch 的 smoke。夹具是合成 K 线。#6 把这些版本放进 `pyproject.toml` 和 `uv.lock`，里面有 pyarrow。",
          "Pins the direct dependencies and adds a one-epoch smoke. The fixture is synthetic bars. #6 put those pins in `pyproject.toml` and `uv.lock`, including pyarrow.",
        ),
      },
      {
        n: "#3",
        href: links.pr3,
        title: "Fix backtest alignment, leakage, and sync the docs",
        state: merged,
        base: L("squash `2b56c06`", "squash `2b56c06`"),
        body: L(
          "改了回测对齐和信息泄漏，补了测试，中英文说明改成和代码一致。上面的切分和缩放就是这份改动。双语文档从这里进了 main。",
          "Changes the backtest alignment and the leakage, adds tests, and rewrites the Chinese and English notes to match the code. The split and scaling above are this change. The bilingual docs entered main here.",
        ),
      },
      {
        n: "#4",
        href: links.pr4,
        title: "Load daily bars from Hive minute Parquet",
        state: merged,
        base: L("squash `d47ba61`", "squash `d47ba61`"),
        body: L(
          "读取 Hive 分钟 Parquet，变量是 `MOE_DATA_PARQUET`、`MOE_SYMBOL`，多份 security 时再加 `MOE_SECURITY`，然后收成日线。CSV 留着作回退。",
          "Reads Hive minute Parquet through `MOE_DATA_PARQUET` and `MOE_SYMBOL`, plus `MOE_SECURITY` when one ticker has several hashes, and rolls the minutes up to daily bars. CSV stays as the fallback.",
        ),
      },
      {
        n: "#5",
        href: links.pr5,
        title: "Add Simplified Chinese README (README.zh-CN.md)",
        state: L("已关闭", "Closed"),
        base: L("未合并", "Not merged"),
        body: L(
          "已经关闭。中英文档随 #3 进了 main。根 README 顶部的语言切换随 #6 进了 main。",
          "Closed. The bilingual docs entered main with #3. The language switch on the root READMEs entered main with #6.",
        ),
      },
      {
        n: "#6",
        href: links.pr6,
        title: "Switch dependency management from pip to uv",
        state: merged,
        base: L("squash `7b8f839`", "squash `7b8f839`"),
        body: L(
          "安装从 pip 换成 uv。`pyproject.toml` 加上 `uv.lock`。`requirements.txt` 删了。当时的运行命令是 `uv sync` 和 `uv run python moe_lstm.py`。smoke 和 unittest 的 CI 跑 `uv sync --frozen`。根 README 的语言切换也在这份里。",
          "Installs move from pip to uv. `pyproject.toml` gains `uv.lock`. `requirements.txt` is removed. The run commands in that change are `uv sync` and `uv run python moe_lstm.py`. Smoke and unit CI run `uv sync --frozen`. The language switch on the root READMEs is in this change.",
        ),
      },
      {
        n: "#7",
        href: links.pr7,
        title: "Add a bilingual Astro brief and GitHub Pages deploy",
        state: merged,
        base: L("squash `37671ab`", "squash `37671ab`"),
        body: L(
          "`site/` 里这份 Astro 简报，加上 GitHub Pages 工作流。地址就是本页。",
          "This Astro brief under `site/`, plus the GitHub Pages workflow. This page is that site.",
        ),
      },
    ],
    note: L(
      "包和引擎适配器都在仓库里。这一页的回测格子空着。",
      "The package and the engine adapter are in the repository. The backtest cells on this page are empty.",
    ),
  },
  next: {
    index: "05",
    heading: L("边界", "Boundary"),
    intro: L(
      "包打出信号。引擎记下成交和账本。这一页的格子空着。",
      "The package emits signals. The engine records fills and the ledger. The cells on this page are empty.",
    ),
    items: [
      {
        term: L("`src/moe_lstm/`", "`src/moe_lstm/`"),
        detail: L(
          "根目录脚本拆进了 `src/moe_lstm/`。运行命令是 `uv run moe-lstm`。导入名是 `moe_lstm`。",
          "The root script now lives in `src/moe_lstm/`. The command is `uv run moe-lstm`. The import name is `moe_lstm`.",
        ),
      },
      {
        term: L("quant-backtest-engine", "quant-backtest-engine"),
        detail: L(
          "信号从 `moe_lstm.signals` 出去。成交和账本走这个库的 `size` 和 `run_sessions`。示例在 `examples/engine_backtest.py`。这一页不印它的输出。",
          "Signals leave through `moe_lstm.signals`. Fills and the ledger go through this library's `size` and `run_sessions`. The example is `examples/engine_backtest.py`. This page leaves that output off.",
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
        label: L("runchengxie/moe-lstm", "runchengxie/moe-lstm"),
        note: L(
          "这个仓库。里面有脚本、`pyproject.toml`、`uv.lock` 和运行说明。",
          "This repository. It holds the script, `pyproject.toml`, `uv.lock`, and the run notes.",
        ),
      },
      {
        href: links.engine,
        label: L("quant-backtest-engine", "quant-backtest-engine"),
        note: L(
          "成交和账本在那边。本仓库用 `examples/engine_backtest.py` 调它的 Python 客户端。依赖写在 `pyproject.toml` 和 `uv.lock`。客户端要从那个仓库安装。",
          "Fills and the ledger live there. This repository calls its Python client from `examples/engine_backtest.py`. Dependencies sit in `pyproject.toml` and `uv.lock`. Install the client from that repository.",
        ),
      },
      {
        href: links.pages,
        label: L("GitHub Pages", "GitHub Pages"),
        note: L(
          "本页。站点和工作流随 #7 进了 main。",
          "This page. The site and the workflow entered main with #7.",
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
    "这些格子是占位。适配器在仓库里。这一页没有存过运行记录。",
    "These cells are placeholders. The adapter is in the repository. The page has no stored run.",
  ),
  chartTitle: L("权益曲线", "Equity"),
  chartEmpty: L("格子空着，没有曲线", "The cell is empty. There is no series."),
  axisY: L("权益", "Equity"),
  axisX: L("测试窗口", "Test windows"),
  tableCaption: L("脚本会打印这些列。格子空着。", "The script prints these columns. The cells are empty."),
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
  emptyMark: "空",
  definitions: L("这些指标的定义写在训练文档里。", "The training note defines these metrics."),
};

export const architecture = {
  kicker: L("结构", "Architecture"),
  heading: L("模型怎么接上", "How the model is wired"),
  lede: L(
    "三个 LSTM 专家读同一段窗口。门控读最后一根。Hive 分钟 Parquet 是主输入。CSV 是回退。",
    "Three LSTM experts read one window. The gate reads the last bar. Hive minute Parquet is the primary input. CSV is the fallback.",
  ),
  dataHeading: L("数据路径", "Data path"),
  data: L(
    "Hive 分钟线是主输入。设上 `MOE_DATA_PARQUET`，再设 `MOE_SYMBOL`。同一代码有多份 security 时再设 `MOE_SECURITY`。分钟线收成日线。Parquet 根目录空着时，脚本读 `MOE_DATA_CSV`。行情文件留在仓库外面。脚本自带的远程 CSV 在 2026-11-05 返回 HTTP 404。用 CSV 时指向本地文件。",
    "Hive minute bars are the primary input. Set `MOE_DATA_PARQUET`, then `MOE_SYMBOL`. Set `MOE_SECURITY` when one ticker has more than one security hash. Minutes roll up to daily bars. When the Parquet root is empty, the script reads `MOE_DATA_CSV`. Price files stay outside the repository. The default remote CSV returned HTTP 404 on 2026-11-05. A CSV run points at a local file.",
  ),
  splitHeading: L("窗口、切分和缩放", "Windows, split, and scaling"),
  split: L(
    "回看是 `LOOKBACK = 5`。窗口用特征行 t-5 到 t-1。标签是 t 到 t+1 的收盘收益。窗口按时间排，前 80% 训练，后 20% 测试。训练段最后 20% 做早停验证。`MinMaxScaler` 只在拟合窗口的特征行上拟合。收益高于 0.2%（`THRESHOLD = 0.002`）记 1。等于 0.2% 记 0。最多 50 个 epoch，batch 16，早停 patience 5。手工特征、K-Means（5 簇）、3×3 SOM 各训练一次，结构相同。预测 1 做多，预测 0 空仓。旁边印着买入持有。",
    "Lookback is `LOOKBACK = 5`. A window uses feature rows t-5 through t-1. The label is the close-to-close return from t to t+1. Windows stay in time order. The first 80% train and the last 20% test. The last 20% of the training block checks early stopping. `MinMaxScaler` fits only the feature rows of the fit windows. A return above 0.2% (`THRESHOLD = 0.002`) is 1. A return equal to 0.2% is 0. Training runs up to 50 epochs, batch size 16, early-stopping patience 5. Manual features, K-Means with 5 clusters, and a 3 by 3 SOM each train once, on the same architecture. Prediction 1 is long. Prediction 0 is flat. Buy and hold is printed beside them.",
  ),
  more: L("列约定、费用、打印的指标写在文档里。", "Column rules, fees, and the printed metrics are in the docs."),
};

export const changelogCopy = {
  title: L("变更", "Changelog"),
  lede: L(
    "合并记录在这一页。",
    "The merge list is on this page.",
  ),
};

export const parquetCommand = `uv sync
export MOE_DATA_PARQUET=/path/to/dataset-root
export MOE_SYMBOL=AAPL
export MPLBACKEND=Agg
uv run moe-lstm`;

export const csvCommand = `export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
uv run moe-lstm`;
