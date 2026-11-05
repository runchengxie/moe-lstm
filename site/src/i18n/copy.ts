export type Locale = "zh" | "en";

export type Localized = Record<Locale, string>;

export const locales: Locale[] = ["zh", "en"];

export const L = (zh: string, en: string): Localized => ({ zh, en });

export const links = {
  repo: "https://github.com/runchengxie/moe_lstm",
  pr2: "https://github.com/runchengxie/moe_lstm/pull/2",
  pr3: "https://github.com/runchengxie/moe_lstm/pull/3",
  pr4: "https://github.com/runchengxie/moe_lstm/pull/4",
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
  footer: L(
    "研究脚本，不提供交易信号。仓库和本站都不放行情。",
    "A research script, with no trading signals. The repository and this site do not host market data.",
  ),
};

export const copy = {
  meta: {
    title: L("moe_lstm · 项目简报", "moe_lstm · project brief"),
    description: L(
      "moe_lstm 的公开项目简报：日频涨跌混合专家 LSTM、数据契约，以及 2026-11-05 仍开放的 pull request。研究脚本，不是交易系统。",
      "Public brief for moe_lstm: a daily up/down mixture-of-experts LSTM, the data contract, and the pull requests still open on 2026-11-05. A research script, not a trading system.",
    ),
  },
  hero: {
    kicker: L("项目简报", "Project brief"),
    title: L("日频下一交易日涨跌的 MoE-LSTM", "A daily MoE-LSTM for the next session"),
    lede: L(
      "三个 LSTM 专家加一个门控，判断下一交易日涨跌。手工特征、K-Means 与 SOM 三个子集各训练一次，并用多空回测对照买入持有。",
      "Three LSTM experts and a gate call the next session up or down. Manual features, K-Means, and a SOM each supply a subset, and a long/short backtest is set against buy and hold.",
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
      {
        tone: "meta" as const,
        text: L(
          "Python 3.12，安装解析到 TensorFlow 2.21.0",
          "Python 3.12, resolve found TensorFlow 2.21.0",
        ),
      },
    ],
    asOf: L(
      "状态写于 2026-11-05（Asia/Shanghai），对应 main 上已合并的 PR #1（`0309d55`）。这几份开放 PR 之后有没有合并，以 GitHub 上的页面为准。",
      "Written 2026-11-05 (Asia/Shanghai), against main after merged PR #1 (`0309d55`). GitHub is the record of whether these open pull requests later merged.",
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
          "按时间取前 80% 的窗口训练、后 20% 测试，最多 50 个 epoch，batch 16，早停 patience 5。当前 main 把测试段同时用作早停的验证集，标准化也在全样本上拟合。PR #3 改的就是这类评估问题，撰写时仍开放。",
          "The first 80% of windows train and the last 20% test, for up to 50 epochs, batch size 16, and early-stopping patience 5. On current main the test windows are also the early-stopping validation set, and scaling is fit on the full sample. PR #3 is the open change for that evaluation behavior.",
        ),
      },
      {
        term: L("运行时", "Runtime"),
        detail: L(
          "根 README 写明在 Python 3.12 上核对过。2026-11-05 一次全新安装解析到 TensorFlow 2.21.0、pandas 3.1.1、scikit-learn 1.9.1。main 的 `requirements.txt` 仍是下界；精确钉版本在 PR #2，撰写时仍开放。",
          "The root README records a check on Python 3.12. A fresh install on 2026-11-05 resolved TensorFlow 2.21.0, pandas 3.1.1, and scikit-learn 1.9.1. `requirements.txt` on main is still lower bounds. Exact pins are the open PR #2.",
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
          "从 `MOE_DATA_CSV` 读入 `Date`、`Open`、`High`、`Low`、`Close/Last`。未设置时用脚本里的默认 URL；该 URL 在 2026-11-05 返回 HTTP 404。",
          "Read `Date`, `Open`, `High`, `Low`, and `Close/Last` from `MOE_DATA_CSV`. Unset, the script uses the default URL in the file. That URL returned HTTP 404 on 2026-11-05.",
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
      "根 README 写明这三次之后，还会用手工特征集再以名称 MOE 训练一次，所以当前 main 一共训练四次。相关热力图只供查看。无界面时建议 `MPLBACKEND=Agg`；当前 main 仍会调用 `plt.show()`。",
      "The root README notes a fourth fit after those three: the manual set is trained again under the name MOE, so current main trains four times. The correlation heatmap is for inspection. On a machine without a display, set `MPLBACKEND=Agg`. Current main still calls `plt.show()`.",
    ),
  },
  data: {
    index: "03",
    heading: L("数据", "Data"),
    intro: L(
      "行情放在仓库外面，用环境变量指过去。价格列要已经是数字：美元符号或千分位会让滚动计算失败。",
      "Keep prices outside the repository and point at them with an environment variable. Price columns must already be numbers. A dollar sign or thousands separator breaks the rolling calculations.",
    ),
    env: [
      {
        name: "MOE_DATA_CSV",
        detail: L(
          "本地 CSV 路径。不设置则请求下面的默认 URL。撰写时该 URL 返回 HTTP 404（`quant_practice_3` 已不在）。",
          "Path to a local CSV. Unset, the script requests the default URL below. At write time that URL returned HTTP 404 (`quant_practice_3` is gone).",
        ),
      },
      {
        name: "MOE_DATA_PARQUET",
        detail: L(
          "PR #4 增加的 Hive 分钟 Parquet 根目录。撰写时这只在开放的 PR #4 里。需要同时设置 `MOE_SYMBOL`；一个代码有多份 security 时再设置 `MOE_SECURITY`。分钟线会聚合成脚本已有的日线列。CSV 路径还保留。",
          "Hive minute-Parquet root added by open PR #4. At write time this lives only on that pull request. Set `MOE_SYMBOL` with it, and `MOE_SECURITY` when one ticker has more than one security hash. Minutes are rolled up to the daily columns the script already uses. The CSV path remains.",
        ),
      },
    ],
    columns: [
      {
        name: "Date",
        rule: L(
          "只用 `%m/%d/%Y`，例如 `01/13/2020`。ISO 日期会解析失败。",
          "Parsed only as `%m/%d/%Y`, for example `01/13/2020`. ISO dates fail to parse.",
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
    runCaption: L("本地运行", "Run locally"),
    runNote: L(
      "依赖的下界在仓库根目录的 `requirements.txt`。更完整的说明在根 README。",
      "Lower-bound dependencies live in the repository root `requirements.txt`. The root README has the longer setup note.",
    ),
    vendor: L(
      "根 README 说明 AlgoSeek 的美股分钟线要用另一套列名，映射放在单独的文件里，脚本按上面的五列读取。PR #4 是按 Hive Parquet 聚合成日线的那条改动。",
      "The root README states that AlgoSeek US equity minute bars use another schema. Map them in a separate file; the script reads the five columns above. PR #4 is the change that aggregates Hive Parquet into daily bars.",
    ),
    defaultUrl: L(
      "默认 URL，撰写时返回 HTTP 404：",
      "Default URL, HTTP 404 at write time:",
    ),
  },
  prs: {
    index: "04",
    heading: L("开放的 pull request", "Open pull requests"),
    intro: L(
      "下面三份在撰写时都是开放的。标题用的是 GitHub 上的英文原题。",
      "All three were open at write time. Titles are the English titles on GitHub.",
    ),
    items: [
      {
        n: "#2",
        href: links.pr2,
        title: "Pin dependency versions and add a one-epoch CI smoke",
        state: L("开放 · 撰写时", "Open at write time"),
        base: L("基分支 main", "Base: main"),
        body: L(
          "把 2026-11-05 在 Python 3.12 上解析到的版本钉死：TensorFlow 2.21.0、Keras 3.15.1、pandas 3.1.1、numpy 2.5.4、scikit-learn 1.9.1、MiniSom 2.3.6、matplotlib 3.11.2、seaborn 0.13.2。另加一轮 epoch 的 GitHub Actions smoke，夹具是合成 K 线。撰写时 smoke 检查为通过。",
          "Pins the versions a clean Python 3.12 resolve produced on 2026-11-05: TensorFlow 2.21.0, Keras 3.15.1, pandas 3.1.1, numpy 2.5.4, scikit-learn 1.9.1, MiniSom 2.3.6, matplotlib 3.11.2, and seaborn 0.13.2. Adds a one-epoch GitHub Actions smoke on a synthetic bar fixture. The smoke check was green at write time.",
        ),
      },
      {
        n: "#3",
        href: links.pr3,
        title: "Fix backtest alignment, leakage, and sync the docs",
        state: L("开放 · 撰写时", "Open at write time"),
        base: L("叠在 #2 上，基分支是 pin 依赖那条分支", "Stacked on #2; base is the pin-deps branch"),
        body: L(
          "修正回测对齐和信息泄漏，并让中英文说明与实际跑起来的代码一致。撰写时 smoke 和 unittest 为通过。建议先合并 #2，再合并 #3。",
          "Corrects backtest alignment and leakage, and rewrites the Chinese and English docs so they match the code that runs. Smoke and unittest were green at write time. Merge #2, then #3.",
        ),
      },
      {
        n: "#4",
        href: links.pr4,
        title: "Load daily bars from Hive minute Parquet",
        state: L("开放 · 撰写时", "Open at write time"),
        base: L("基分支 main，可与 #2 并列合并", "Base: main; can merge beside #2"),
        body: L(
          "从 main 拉出。读取 Hive 分钟 Parquet（`MOE_DATA_PARQUET`、`MOE_SYMBOL`，必要时 `MOE_SECURITY`）并聚合成日线。撰写时 parquet-loader 检查为通过。它和 #2 都会改 `requirements.txt`：保留 #2 的钉版本，并加上 pyarrow。",
          "Branched from main. Reads Hive minute Parquet (`MOE_DATA_PARQUET`, `MOE_SYMBOL`, and `MOE_SECURITY` when needed) and aggregates it to daily bars. The parquet-loader check was green at write time. It and #2 both edit `requirements.txt`: keep #2's pins and add pyarrow.",
        ),
      },
    ],
    order: L(
      "建议的合并顺序：先 #2，再 #3。#4 基于 main，可以和 #2 并列合并。",
      "Suggested merge order: #2, then #3. #4 is based on main and can merge beside #2.",
    ),
  },
  links: {
    index: "05",
    heading: L("链接", "Links"),
    items: [
      {
        href: links.repo,
        label: L("runchengxie/moe_lstm", "runchengxie/moe_lstm"),
        note: L("本仓库。脚本、依赖和运行说明。", "This repository. Script, dependencies, and how to run it."),
      },
      {
        href: links.pr2,
        label: L("PR #2", "PR #2"),
        note: L("钉依赖，并加一轮 epoch 的 smoke。", "Pin dependencies and add a one-epoch smoke."),
      },
      {
        href: links.pr3,
        label: L("PR #3", "PR #3"),
        note: L("回测对齐、泄漏和文档。叠在 #2 上。", "Backtest alignment, leakage, and docs. Stacked on #2."),
      },
      {
        href: links.pr4,
        label: L("PR #4", "PR #4"),
        note: L("Hive Parquet 日线。从 main 拉出。", "Hive Parquet daily bars. Branched from main."),
      },
      {
        href: links.engine,
        label: L("quant-backtest-engine", "quant-backtest-engine"),
        note: L(
          "独立的 Rust 回测库和命令行，留作以后的回测参考。本脚本的 `requirements.txt` 只列 Python 包。",
          "A separate Rust backtest library and CLI, kept as a future backtest reference. This script's `requirements.txt` lists the Python packages only.",
        ),
      },
      {
        href: links.pages,
        label: L("GitHub Pages", "GitHub Pages"),
        note: L(
          "启用 Actions 部署并在 main 上成功发布之后的地址。撰写时该地址返回 HTTP 404。",
          "Address after a successful Actions deploy on main. It returned HTTP 404 at write time.",
        ),
      },
    ],
  },
  missing: {
    title: L("没有这一页", "No such page"),
    body: L("简报只有首页。", "The brief is a single page."),
    home: L("回到简报", "Back to the brief"),
  },
};

export const runCommand = `export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
python moe_lstm.py`;
