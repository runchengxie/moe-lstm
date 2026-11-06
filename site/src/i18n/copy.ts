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
  pr8: "https://github.com/runchengxie/moe-lstm/pull/8",
  pr9: "https://github.com/runchengxie/moe-lstm/pull/9",
  pr10: "https://github.com/runchengxie/moe-lstm/pull/10",
  pr11: "https://github.com/runchengxie/moe-lstm/pull/11",
  pr12: "https://github.com/runchengxie/moe-lstm/pull/12",
  pr13: "https://github.com/runchengxie/moe-lstm/pull/13",
  pr14: "https://github.com/runchengxie/moe-lstm/pull/14",
  pr15: "https://github.com/runchengxie/moe-lstm/pull/15",
  pr16: "https://github.com/runchengxie/moe-lstm/pull/16",
  pr17: "https://github.com/runchengxie/moe-lstm/pull/17",
  pr18: "https://github.com/runchengxie/moe-lstm/pull/18",
  pr19: "https://github.com/runchengxie/moe-lstm/pull/19",
  pr20: "https://github.com/runchengxie/moe-lstm/pull/20",
  pr21: "https://github.com/runchengxie/moe-lstm/pull/21",
  pr22: "https://github.com/runchengxie/moe-lstm/pull/22",
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
const closed = L("已关闭", "Closed");

export const copy = {
  meta: {
    title: L("moe_lstm 回测和结构", "moe_lstm results and architecture"),
    description: L(
      "首页是 2026-11-06 的 SPY 日线运行。稀疏 top-1 是主结果，三个模型都空仓。稠密对照的硬标签也是空仓。页面也写下门控、Hive Parquet，以及 CSV 回退。",
      "The home page is the 2026-11-06 SPY daily run. Sparse top-1 is the featured result, and all three models stayed flat. The dense ablation has the same hard labels. The page also describes the gate, Hive Parquet, and the CSV fallback.",
    ),
  },
  hero: {
    kicker: L("研究脚本", "Research script"),
    title: L("下一交易日收益的 MoE-LSTM", "An MoE-LSTM for the next session's return"),
    lede: L(
      "三个 LSTM 专家读同一段窗口。默认门控是 top-1。下面的格子是 2026-11-06 的 SPY 日线运行。",
      "Three LSTM experts read one window. The default gate is top-1. The cells below are the 2026-11-06 SPY daily run.",
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
      "写于 2026-11-06（Asia/Shanghai），对应 main 的 `3f02207`（#22 的 squash）。数字来自代码 `5cf5003`。标的是 SPY 日线，2020-01-13 到 2025-01-10，共 1257 根。这是仓库外准备的公开 CSV。原文件日期是 ISO，脚本只认 `%m/%d/%Y`，所以运行前只改了日期，价格没动。原 CSV 不在 git 里。稀疏 top-1 是主表。稠密 softmax 是对照。两次各跑了 21 秒。",
      "Written 2026-11-06 (Asia/Shanghai), against main at `3f02207` (the squash of #22). The figures come from code `5cf5003`. The series is SPY daily, 13 Jan 2020 to 10 Jan 2025, 1,257 bars. It is a public CSV prepared outside the repository. The source dates are ISO. The loader accepts only `%m/%d/%Y`, so the run rewrote the dates and left the prices unchanged. The raw CSV is not in git. Sparse top-1 is the featured table. Dense softmax is the comparison. Each run took 21 seconds.",
    ),
  },
  what: {
    index: "01",
    heading: L("是什么", "What it is"),
    facts: [
      {
        term: L("标的", "Subject"),
        detail: L(
          "脚本按指数点位写，看下一交易日涨跌。首页的 SPY 日线是 2020-01-13 到 2025-01-10。稀疏 top-1 是主表。稠密 softmax 是对照。",
          "The script is written for an index level and the next session's direction. The home-page series is SPY daily, 13 Jan 2020 to 10 Jan 2025. Sparse top-1 is the featured table. Dense softmax is the comparison.",
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
          "三个 LSTM（各 64 单元，保留时间维）展平后堆在一起。路由是宽度为 3 的 softmax，只看输入的最后一根。默认是 top-1。选中的专家权重为 1，另外两个为 0，再做加权求和。`MOE_TOP_K=dense` 时三个权重都保留。后面接 sigmoid，概率大于 0.5 判为涨。任务损失是 binary crossentropy，优化器是 Adam。稀疏路径另加一项负载均衡辅助损失，系数 0.01。专家是 LSTM。门控只读最后一根。",
          "Three LSTMs (64 units, sequences kept) are flattened and stacked. The router is a width-3 softmax on the last input bar only. The default is top-1: the selected expert has weight 1, the other two have weight 0, and those weights form the sum. `MOE_TOP_K=dense` keeps all three weights. A sigmoid follows. A probability above 0.5 is up. The task loss is binary crossentropy. The optimizer is Adam. The sparse path adds a load-balancing auxiliary term with coefficient 0.01. These are LSTM experts, not a Transformer MoE.",
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
          "根 README 写明在 Python 3.12 上核对过。安装用 uv 0.13.7。`uv sync` 读取 `pyproject.toml` 和 `uv.lock`。直接依赖钉到 TensorFlow 2.21.0、Keras 3.15.1、pandas 3.1.1、numpy 2.5.4、scikit-learn 1.9.1、MiniSom 2.3.6、matplotlib 3.11.2、seaborn 0.13.2、pyarrow 26.0.1。`requirements.txt` 已随 #6 删除。smoke 和 unittest 的 CI 使用 `uv sync --frozen`。",
          "The root README records a check on Python 3.12. Install with uv 0.13.7: `uv sync` reads `pyproject.toml` and `uv.lock`. Direct pins are TensorFlow 2.21.0, Keras 3.15.1, pandas 3.1.1, numpy 2.5.4, scikit-learn 1.9.1, MiniSom 2.3.6, matplotlib 3.11.2, seaborn 0.13.2, and pyarrow 26.0.1. `requirements.txt` was removed in #6. Smoke and unit CI run `uv sync --frozen`.",
        ),
      },
    ],
  },
  arch: [
    { n: "1", k: L("输入", "Input"), v: L("5 根 × 选定列", "5 bars × selected columns") },
    { n: "2", k: L("专家", "Experts"), v: L("LSTM × 3，各 64", "LSTM × 3, 64 each") },
    { n: "3", k: L("门控", "Gate"), v: L("默认 top-1，未选中为 0", "Default top-1. Unselected weights are 0") },
    { n: "4", k: L("输出", "Output"), v: L("sigmoid，阈值 0.5", "sigmoid, cutoff 0.5") },
  ],
  pipeline: {
    index: "02",
    heading: L("流程", "Pipeline"),
    steps: [
      {
        name: L("OHLCV", "OHLCV"),
        detail: L(
          "设置了 `MOE_DATA_PARQUET` 时读取 Hive 分钟 Parquet，并聚合成日线，还要设置 `MOE_SYMBOL`。未设置时从 `MOE_DATA_CSV` 读入 `Date`、`Open`、`High`、`Low`、`Close/Last`。CSV 也未设置时用脚本里的默认 URL。该 URL 在 2026-11-05 返回 HTTP 404，2026-11-06 再查仍是 404。",
          "When `MOE_DATA_PARQUET` is set, the script reads Hive minute Parquet and rolls it up to daily bars, and `MOE_SYMBOL` is required. Otherwise it reads `Date`, `Open`, `High`, `Low`, and `Close/Last` from `MOE_DATA_CSV`. If that is also unset, it uses the default URL in the file. That URL returned HTTP 404 on 2026-11-05, and it still did on 2026-11-06.",
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
          "Manual、KMeans、SOM 三个子集各训练一次同一个结构。结构是三个 LSTM 专家。默认 top-1，没选中的权重是 0。`MOE_TOP_K=dense` 仍把三个 softmax 加在一起。",
          "Manual, KMeans, and SOM each train the same architecture once: three LSTM experts. The default is top-1, and unselected weights are 0. `MOE_TOP_K=dense` still adds the three softmax weights.",
        ),
      },
      {
        name: L("回测", "Backtest"),
        detail: L(
          "测试段上，预测为 1 则做多，为 0 则空仓，并与买入持有对照。类别 0 里有小涨。脚本打印 accuracy、precision、recall、F1、AUC-ROC、总收益、最大回撤，以及按 √252 年化的夏普。样本外的日期和概率写在 `oos_probabilities.csv`。首页记下了 2026-11-06 的 SPY 运行，稀疏 top-1 是主表，稠密是对照。",
          "On the test slice, a prediction of 1 is long and a prediction of 0 is flat, compared with buy and hold. Class 0 includes small gains. The script prints accuracy, precision, recall, F1, AUC-ROC, total return, max drawdown, and a Sharpe ratio annualized with √252. Out-of-sample dates and probabilities are written to `oos_probabilities.csv`. The home page records the 2026-11-06 SPY run. Sparse top-1 is the main table. Dense is the comparison.",
        ),
      },
    ],
    note: L(
      "一次运行训练三个模型。它们是手工特征、K-Means 子集、SOM 子集。相关热力图只供查看，仍使用全样本。`MPLBACKEND=Agg` 时画出图后关闭，不调用 `plt.show()`。交互式后端仍会调用 `plt.show()`。",
      "One run fits three models: manual features, the K-Means subset, and the SOM subset. The correlation heatmap is for inspection and still uses the full sample. With `MPLBACKEND=Agg` the script draws the figures and closes them, and does not call `plt.show()`. An interactive backend still calls `plt.show()`.",
    ),
  },
  data: {
    index: "03",
    heading: L("数据", "Data"),
    intro: L(
      "行情放在仓库外面。主路径是 Hive 分钟 Parquet。未设置时回退到 CSV。价格列要已经是数字。美元符号或千分位会让滚动计算失败。",
      "Keep prices outside the repository. Hive minute Parquet is the primary path; CSV is the fallback when that root is unset. Price columns must already be numbers. A dollar sign or thousands separator breaks the rolling calculations.",
    ),
    env: [
      {
        name: "MOE_DATA_PARQUET",
        detail: L(
          "已在 main（#4）。Hive 分钟 Parquet 根目录。需要同时设置 `MOE_SYMBOL`。一个代码有多份 security 时再设置 `MOE_SECURITY`。设置之后优先于 `MOE_DATA_CSV`。分钟线聚合成脚本已有的日线列。不设置时仍走 CSV。",
          "On main since #4. Hive minute-Parquet root. Set `MOE_SYMBOL` with it, and `MOE_SECURITY` when one ticker has more than one security hash. When set, it wins over `MOE_DATA_CSV`. Minutes are rolled up to the daily columns the script already uses. Unset, the script still reads CSV.",
        ),
      },
      {
        name: "MOE_DATA_CSV",
        detail: L(
          "Parquet 根目录未设置时的日频 CSV，可以是本地路径或 `pandas.read_csv` 能打开的 URL。这一项和 Parquet 都未设置时，脚本请求下面的默认 URL。2026-11-05 该 URL 返回 HTTP 404，2026-11-06 再查仍是 404。`quant_practice_3` 里已经没有这个文件。",
          "Daily CSV used when the Parquet root is unset. A local path or any URL `pandas.read_csv` can open. If this and the Parquet root are both unset, the script requests the default URL below. That URL returned HTTP 404 on 2026-11-05, and it still did on 2026-11-06 (`quant_practice_3` is gone).",
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
      "`docs/data.zh-CN.md` 写着 AlgoSeek 美股 bar 用另一套列名。在单独的文件里映射成这五列。Hive 分钟 Parquet 是 main 上的另一条路径。加载器把分钟字段收成这些日线列。Parquet 根目录空着时，脚本读 CSV。",
      "`docs/data.md` says AlgoSeek US equity bars use other column names. Map them onto these five columns in a separate file. Hive minute Parquet is another path already on main. The loader rolls minute fields up to these daily columns. When the Parquet root is empty, the script reads CSV.",
    ),
    defaultUrl: L(
      "默认 CSV URL 在 2026-11-05 返回 HTTP 404，2026-11-06 再查仍是 404。",
      "Default CSV URL. It returned HTTP 404 on 2026-11-05, and it still did on 2026-11-06.",
    ),
  },
  merged: {
    index: "04",
    heading: L("已在 main", "On main"),
    intro: L(
      "按编号列到 #22。已合并的都是 squash 进 main。标题是 GitHub 上的英文原题。",
      "Listed by number through #22. Merged items were squash-merged into main. Titles are the English titles on GitHub.",
    ),
    items: [
      {
        n: "#1",
        href: links.pr1,
        title: "Fix fresh-run blockers in the MoE-LSTM script",
        state: merged,
        base: L("squash `0309d55`", "squash `0309d55`"),
        body: L(
          "让本地 CSV 能够启动训练。",
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
          "已关闭。准确的中英文档随 #3 进入 main。根 README 顶部的语言切换随 #6 进入 main。",
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
          "安装从 pip 换成 uv。`pyproject.toml` 加上 `uv.lock`，`requirements.txt` 删除。当时的命令是 `uv run python moe_lstm.py`。现在的命令是 `uv run moe-lstm`，见 #17。smoke 与 unittest 的 CI 使用 `uv sync --frozen`。根 README 的语言切换也在这份里。",
          "Switches installs from pip to uv. `pyproject.toml` plus `uv.lock`, and `requirements.txt` removed. The command in that change was `uv run python moe_lstm.py`. The current command is `uv run moe-lstm`, from #17. Smoke and unit CI use `uv sync --frozen`. The language switcher on the root READMEs is in this change.",
        ),
      },
      {
        n: "#7",
        href: links.pr7,
        title: "Add a bilingual Astro brief and GitHub Pages deploy",
        state: merged,
        base: L("squash `37671ab`", "squash `37671ab`"),
        body: L(
          "`site/` 下的这份 Astro 简报，以及 GitHub Pages 工作流。站点已经发布。",
          "This Astro brief under `site/`, and the GitHub Pages workflow. The site is published.",
        ),
      },
      {
        n: "#8",
        href: links.pr8,
        title: "Simplify the root READMEs and move technical detail into docs",
        state: merged,
        base: L("squash `3350aeb`", "squash `3350aeb`"),
        body: L(
          "根 README 收短，技术细节挪进 `docs/`。",
          "Shortens the root READMEs and moves the technical detail into `docs/`.",
        ),
      },
      {
        n: "#9",
        href: links.pr9,
        title: "Update the site brief to match merged main",
        state: merged,
        base: L("squash `fa82ee7`", "squash `fa82ee7`"),
        body: L(
          "站点简报改到当时的 main。",
          "Updates the site brief to the main of that day.",
        ),
      },
      {
        n: "#10",
        href: links.pr10,
        title: "Make the site home a backtest placeholder and architecture view",
        state: merged,
        base: L("squash `d38c878`", "squash `d38c878`"),
        body: L(
          "首页当时是回测占位和模型结构。发布的数字是 #22 的 SPY 运行。",
          "The home page was a backtest placeholder and the model layout. The published figures are the SPY run from #22.",
        ),
      },
      {
        n: "#11",
        href: links.pr11,
        title: "Point the project site at the moe-lstm Pages path",
        state: merged,
        base: L("squash `07a6b8d`", "squash `07a6b8d`"),
        body: L(
          "站点地址改到 `/moe-lstm/`。",
          "Points the project site at the `/moe-lstm/` Pages path.",
        ),
      },
      {
        n: "#12",
        href: links.pr12,
        title: "Split the study script into the moe_lstm package",
        state: closed,
        base: L("未合并", "Not merged"),
        body: L(
          "已关闭。同一件事在 #17 合并。",
          "Closed. The same work merged as #17.",
        ),
      },
      {
        n: "#13",
        href: links.pr13,
        title: "Send study signals through quant-backtest-engine",
        state: closed,
        base: L("未合并", "Not merged"),
        body: L(
          "已关闭。同一件事在 #18 合并。",
          "Closed. The same work merged as #18.",
        ),
      },
      {
        n: "#14",
        href: links.pr14,
        title: "Correct drawdown and the flat label",
        state: closed,
        base: L("未合并", "Not merged"),
        body: L(
          "已关闭。同一件事在 #16 合并。",
          "Closed. The same work merged as #16.",
        ),
      },
      {
        n: "#15",
        href: links.pr15,
        title: "Rewrite the site and docs in plain sentences",
        state: closed,
        base: L("未合并", "Not merged"),
        body: L(
          "已关闭。站点文案的改写在 #19 合并。",
          "Closed. The site-copy rewrite merged as #19.",
        ),
      },
      {
        n: "#16",
        href: links.pr16,
        title: "Correct drawdown, flat labels, and save OOS probabilities",
        state: merged,
        base: L("squash `dff5e28`", "squash `dff5e28`"),
        body: L(
          "修正最大回撤和空仓标签。测试段的日期和概率写入 `oos_probabilities.csv`。",
          "Corrects max drawdown and the flat label. Test dates and probabilities are written to `oos_probabilities.csv`.",
        ),
      },
      {
        n: "#17",
        href: links.pr17,
        title: "Split the corrected script into the moe_lstm package",
        state: merged,
        base: L("squash `db7c746`", "squash `db7c746`"),
        body: L(
          "根目录脚本拆进 `src/moe_lstm/`。命令是 `uv run moe-lstm`。",
          "Splits the root script into `src/moe_lstm/`. The command is `uv run moe-lstm`.",
        ),
      },
      {
        n: "#18",
        href: links.pr18,
        title: "Send study signals through quant-backtest-engine",
        state: merged,
        base: L("squash `db5c6a5`", "squash `db5c6a5`"),
        body: L(
          "信号从 `moe_lstm.signals` 出去。成交和账本走 quant-backtest-engine 的 `size` 和 `run_sessions`。",
          "Signals leave through `moe_lstm.signals`. Fills and the ledger go through quant-backtest-engine `size` and `run_sessions`.",
        ),
      },
      {
        n: "#19",
        href: links.pr19,
        title: "Rewrite the visible site copy in plain sentences",
        state: merged,
        base: L("squash `b728d3c`", "squash `b728d3c`"),
        body: L(
          "可见的站点文案改成短句。",
          "Rewrites the visible site copy into short sentences.",
        ),
      },
      {
        n: "#20",
        href: links.pr20,
        title: "Add a sparse top-k gate beside the dense LSTM mixture",
        state: merged,
        base: L("squash `2254a46`", "squash `2254a46`"),
        body: L(
          "默认门控是稀疏 top-1。选中的专家权重为 1，另外两个为 0。`MOE_TOP_K=dense` 保留三个专家的 softmax。",
          "The default gate is sparse top-1. The selected expert has weight 1 and the other two have weight 0. `MOE_TOP_K=dense` keeps the softmax over all three.",
        ),
      },
      {
        n: "#21",
        href: links.pr21,
        title: "Publish the ^GSPC study run on the project site",
        state: merged,
        base: L("squash `5cf5003`", "squash `5cf5003`"),
        body: L(
          "首页记下 2026-11-06 的 ^GSPC 日线运行。三个模型都空仓。#22 把首页换成 SPY。",
          "Publishes the 2026-11-06 ^GSPC daily run on the home page. All three models stayed flat. #22 replaces that home page with SPY.",
        ),
      },
      {
        n: "#22",
        href: links.pr22,
        title: "Publish the SPY 2020-2025 study run",
        state: merged,
        base: L("squash `3f02207`", "squash `3f02207`"),
        body: L(
          "首页是 SPY 日线，2020-01-13 到 2025-01-10，共 1257 根。稀疏 top-1 是主表。稠密 softmax 是对照。三个模型的硬预测都是空仓。",
          "The home page is SPY daily bars, 13 Jan 2020 to 10 Jan 2025, 1,257 sessions. Sparse top-1 is the featured table. Dense softmax is the comparison. Every hard prediction is flat.",
        ),
      },
    ],
    note: L(
      "main 现在在 `3f02207`（#22）。包和引擎适配器都在仓库里。首页记下了 2026-11-06 的 SPY 运行。稀疏 top-1 是主表。稠密是对照。",
      "main is at `3f02207` (#22). The package and the engine adapter are in the repository. The home page records the 2026-11-06 SPY run. Sparse top-1 is the featured table. Dense is the comparison.",
    ),
  },
  next: {
    index: "05",
    heading: L("包和引擎", "Package and engine"),
    intro: L(
      "包打出信号。引擎记下成交和账本。首页格子是研究脚本自己的回测。引擎账本留在引擎那边。",
      "The package emits signals. The engine records fills and the ledger. The cells on the home page are the study script's own backtest. The engine ledger stays with the engine.",
    ),
    items: [
      {
        term: L("`src/moe_lstm/`", "`src/moe_lstm/`"),
        detail: L(
          "根目录脚本已经拆成这个包。运行是 `uv run moe-lstm`。导入名是 `moe_lstm`。",
          "The root script is this package. Run it with `uv run moe-lstm`. The import name is `moe_lstm`.",
        ),
      },
      {
        term: L("quant-backtest-engine", "quant-backtest-engine"),
        detail: L(
          "信号从 `moe_lstm.signals` 出去。成交和账本走 `size` 和 `run_sessions`。示例是 `examples/engine_backtest.py`。首页留下研究脚本的回测。",
          "Signals leave through `moe_lstm.signals`. Fills and the ledger go through `size` and `run_sessions`. The example is `examples/engine_backtest.py`. This page leaves that output off.",
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
          "本仓库。脚本、`pyproject.toml`、`uv.lock` 和运行说明。",
          "This repository. Script, `pyproject.toml`, `uv.lock`, and how to run it.",
        ),
      },
      {
        href: links.engine,
        label: L("quant-backtest-engine", "quant-backtest-engine"),
        note: L(
          "回测库已接上。信号从 `moe_lstm.signals` 出去，成交和账本走 `size` 和 `run_sessions`。本仓库的依赖在 `pyproject.toml` 和 `uv.lock`。",
          "The backtest library is wired up. Signals leave through `moe_lstm.signals`. Fills and the ledger go through `size` and `run_sessions`. This repository's dependencies are in `pyproject.toml` and `uv.lock`.",
        ),
      },
      {
        href: links.pages,
        label: L("GitHub Pages", "GitHub Pages"),
        note: L(
          "站点已经发布。工作流随 #7 进入 main。首页的 SPY 运行随 #22 进入 main。",
          "The site is published. The workflow landed on main with #7. The SPY run on the home page landed with #22.",
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
  heading: L("这一次运行", "This run"),
  empty: L(
    "SPY 日线，2020-01-13 到 2025-01-10，共 1257 根。测试段 247 个窗口，标签日从 2024-01-17 到 2025-01-08。主表是稀疏 top-1。三个模型的 sigmoid 都低于 0.5，预测全是 0，所以一直空仓。买入持有用同一段向前收益，费用是 0。稠密 softmax 另跑了一次，硬预测也全是空仓，AUC 写在对照表里。",
    "SPY daily bars, 13 Jan 2020 to 10 Jan 2025, 1,257 sessions. The test slice is 247 windows, with label dates from 17 Jan 2024 to 8 Jan 2025. The main table is sparse top-1. Every sigmoid score is below 0.5, so every prediction is 0 and the position stays flat. Buy and hold uses the same forward returns with fee 0. A dense softmax run has the same hard labels. Its AUC is in the comparison table.",
  ),
  chartTitle: L("权益曲线", "Equity"),
  chartNote: L(
    "三条模型曲线重合在 1 上。图按 `equity.csv` 重画，颜色跟这一页一致。脚本自己存下的图是 `equity.png`。",
    "The three model curves sit on 1. This picture is redrawn from `equity.csv` in the colors of this page. The figure the script saved is `equity.png`.",
  ),
  confusionTitle: L("混淆矩阵", "Confusion"),
  confusionNote: L(
    "这是稀疏 top-1 的混淆矩阵。预测为 Above 的格子都是 0。真值里 139 个 Not above，108 个 Above。",
    "This is the sparse top-1 confusion matrix. The Predicted Above column is 0. The truth column is 139 Not above and 108 Above.",
  ),
  tableCaption: L(
    "稀疏 top-1，和那次运行 `round(3)` 的打印一致。策略收益是常数时，夏普率是 NaN。买入持有没有分类分数。",
    "Sparse top-1, matching that run's `round(3)` print. Sharpe is NaN when the strategy return is constant. Buy and hold has no class scores.",
  ),
  runMeta: L(
    "主结果是稀疏 top-1，辅助损失系数 0.01。最多 50 个 epoch，早停耐心 5，批大小 16，费用 0.0005，标签阈值 0.002，回看 5。这次 K-Means 留下 RSI、EMA5、MACD、Volatility、Daily_Return。SOM 留下 Low、Volatility。稠密对照用 `MOE_TOP_K=dense`，不加辅助损失。",
    "The featured result is sparse top-1, auxiliary loss weight 0.01. Up to 50 epochs, early-stopping patience 5, batch size 16, fee 0.0005, label threshold 0.002, lookback 5. On this run K-Means kept RSI, EMA5, MACD, Volatility, and Daily_Return. SOM kept Low and Volatility. The dense comparison uses `MOE_TOP_K=dense` and adds no auxiliary loss.",
  ),
  denseHeading: L("稠密对照", "Dense comparison"),
  denseCaption: L(
    "同一次数据上的 `MOE_TOP_K=dense`。硬预测也全是空仓，所以收益、回撤和夏普与上面相同。AUC 不同。",
    "The same data with `MOE_TOP_K=dense`. The hard predictions are also all flat, so return, drawdown, and Sharpe match the table above. AUC does not.",
  ),
  filesLabel: L("这次运行的文件。", "Files from this run: "),
  modelHeading: L("模型", "Model"),
  models: [
    {
      id: "manual",
      name: "Manual",
      values: {
        accuracy: "0.563",
        precision: "0.0",
        recall: "0.0",
        f1: "0.0",
        "auc-roc": "0.539",
        "total-return": "0.0",
        "max-drawdown": "0.0",
        sharpe: "NaN",
      },
    },
    {
      id: "kmeans",
      name: "KMeans",
      values: {
        accuracy: "0.563",
        precision: "0.0",
        recall: "0.0",
        f1: "0.0",
        "auc-roc": "0.547",
        "total-return": "0.0",
        "max-drawdown": "0.0",
        sharpe: "NaN",
      },
    },
    {
      id: "som",
      name: "SOM",
      values: {
        accuracy: "0.563",
        precision: "0.0",
        recall: "0.0",
        f1: "0.0",
        "auc-roc": "0.529",
        "total-return": "0.0",
        "max-drawdown": "0.0",
        sharpe: "NaN",
      },
    },
    {
      id: "buy-hold",
      name: "Buy & hold",
      values: {
        accuracy: "—",
        precision: "—",
        recall: "—",
        f1: "—",
        "auc-roc": "—",
        "total-return": "0.229",
        "max-drawdown": "-0.084",
        sharpe: "1.711",
      },
    },
  ],
  denseModels: [
    {
      id: "manual-dense",
      name: "Manual",
      values: {
        accuracy: "0.563",
        precision: "0.0",
        recall: "0.0",
        f1: "0.0",
        "auc-roc": "0.543",
        "total-return": "0.0",
        "max-drawdown": "0.0",
        sharpe: "NaN",
      },
    },
    {
      id: "kmeans-dense",
      name: "KMeans",
      values: {
        accuracy: "0.563",
        precision: "0.0",
        recall: "0.0",
        f1: "0.0",
        "auc-roc": "0.547",
        "total-return": "0.0",
        "max-drawdown": "0.0",
        sharpe: "NaN",
      },
    },
    {
      id: "som-dense",
      name: "SOM",
      values: {
        accuracy: "0.563",
        precision: "0.0",
        recall: "0.0",
        f1: "0.0",
        "auc-roc": "0.531",
        "total-return": "0.0",
        "max-drawdown": "0.0",
        sharpe: "NaN",
      },
    },
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
  definitions: L(
    "指标怎么定义，写在训练文档里。完整小数在 `run.json`。",
    "How the metrics are defined is in the training note. Full precision is in `run.json`.",
  ),
};

export const architecture = {
  kicker: L("结构", "Architecture"),
  heading: L("模型怎么接在一起", "How the model is put together"),
  lede: L(
    "三个 LSTM 专家读同一段窗口。路由只看最后一根。默认只把权重留给 top-1 的那个专家，另外两个权重是 0。数据以 Hive 分钟 Parquet 为主，CSV 是回退。",
    "Three LSTM experts read the same window. The router sees only the last bar. By default only the top expert keeps a weight, and the other two are 0. Hive minute Parquet is the primary input. CSV is the fallback.",
  ),
  flow: [
    { n: "1", k: L("窗口", "Window"), v: L("三个 LSTM 读同一段 5 根", "Three LSTMs read the same 5 bars") },
    { n: "2", k: L("路由", "Router"), v: L("只看最后一根，softmax 成 3 个数", "Last bar only, softmax to 3 numbers") },
    {
      n: "3",
      k: L("top-k", "top-k"),
      v: L("默认留下 1 个专家，权重为 1，其余为 0", "Default keeps 1 expert at weight 1. The rest are 0"),
    },
    { n: "4", k: L("输出", "Output"), v: L("加权求和后过 sigmoid", "Weighted sum, then a sigmoid") },
  ],
  sparseNote: L(
    "没选中的专家权重是 0，不进入求和。`MOE_TOP_K=dense` 时三个 softmax 权重都留下。专家是 LSTM。门控只读最后一根。",
    "An expert that is not selected stays out of the sum, at weight 0. `MOE_TOP_K=dense` keeps all three softmax weights. The experts are LSTMs, not a token-wise Transformer MoE.",
  ),
  dataHeading: L("数据路径", "Data path"),
  data: L(
    "设置 `MOE_DATA_PARQUET` 时，Hive 分钟线是主输入，并要有 `MOE_SYMBOL`。同一代码有多份 security 时再设 `MOE_SECURITY`。分钟线收成日线。未设置 Parquet 根目录时回退到 `MOE_DATA_CSV`。仓库里没有行情。脚本自带的远程 CSV 在 2026-11-05 返回 HTTP 404，2026-11-06 再查仍是 404，所以 CSV 需要本地路径。",
    "When `MOE_DATA_PARQUET` is set, Hive minute bars are the primary input, together with `MOE_SYMBOL`, and `MOE_SECURITY` when one ticker has more than one security hash. Minutes roll up to daily bars. `MOE_DATA_CSV` is the fallback when that Parquet root is unset. The repository has no market data. The default remote CSV returned HTTP 404 on 2026-11-05, and it still did on 2026-11-06, so a CSV run needs a local path.",
  ),
  splitHeading: L("窗口、切分和缩放", "Windows, split, and scaling"),
  split: L(
    "回看 `LOOKBACK = 5`。窗口是特征行 t-5 到 t-1，标签是 t 到 t+1 的收盘收益。按时间，前 80% 的窗口训练，后 20% 测试。训练段最后 20% 做早停验证。`MinMaxScaler` 只在拟合窗口的特征行上拟合。标签高于 0.2%（`THRESHOLD = 0.002`）为 1，等于 0.2% 为 0。最多 50 个 epoch，batch 16，早停 patience 5。手工特征、K-Means（5 簇）、3×3 SOM 三个子集各训练一次同一结构。默认门控是稀疏 top-1，选中的专家权重为 1。`MOE_TOP_K=dense` 时三个专家按 softmax 一起加权。预测 1 做多，0 空仓，对照买入持有。",
    "Lookback is `LOOKBACK = 5`. A window is feature rows t-5 through t-1, and the label is the close-to-close return from t to t+1. In time order, the first 80% of windows train and the last 20% test. The last 20% of the training block is the early-stopping validation set. `MinMaxScaler` is fit only on the feature rows of the fit windows. The label is 1 when that return is above 0.2% (`THRESHOLD = 0.002`), and 0 when it is equal to 0.2%. Up to 50 epochs, batch size 16, early-stopping patience 5. Manual features, K-Means (5 clusters), and a 3×3 SOM each train that same architecture once. The default gate is sparse top-1, so the selected expert has weight 1. `MOE_TOP_K=dense` weights all three experts with the softmax. A prediction of 1 is long and 0 is flat, set against buy and hold.",
  ),
  more: L("列约定、费用和打印的指标在文档里。", "Column rules, fees, and the printed metrics are in the docs."),
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


export const migration = {
  title: L("项目已迁入 Global Market Research", "Research has moved to Global Market Research"),
  body: L("LSTM/MoE 后续开发、实验和交互图表在新项目维护。这里保留原始实现和历史 SPY 结果，不代表新研究的最新状态。", "LSTM/MoE development, experiments and interactive charts now live in the new project. This site preserves the original implementation and historical SPY results, rather than the latest research state."),
  open: L("前往新研究页面", "Open the new research page"),
  repo: L("查看新项目源码", "View the new project source"),
  timer: L("首页将在 15 秒后跳转。历史文档和结果链接继续保留，也可以取消跳转查看下方旧内容。", "This home page opens the new research page after 15 seconds. Historical documentation and result links remain available; cancel to read the old content below."),
  cancel: L("留在历史页面", "Stay on the historical page"),
  stopped: L("已取消自动跳转，可随时使用上方链接前往新项目。", "Automatic navigation canceled. The links above remain available."),
};
