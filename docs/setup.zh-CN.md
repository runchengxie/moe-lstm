[English](setup.md) | 简体中文

# 环境

[项目说明](../README.zh-CN.md) · [数据](data.zh-CN.md) · [训练和回测](training.zh-CN.md) · [CI 和项目站点](ci.zh-CN.md)

核对用的是 Python 3.12。先安装 [uv](https://docs.astral.sh/uv/) 0.13.7，再在这个目录执行下面的命令。

```bash
uv sync
```

`uv sync` 创建 `.venv`，装上锁住的依赖，再装上这个项目。导入名是 `moe_lstm`，目录是 `src/moe_lstm/`。控制台命令是 `moe-lstm`。`python -m moe_lstm` 跑同一次研究。`pyproject.toml` 钉住直接依赖。`uv.lock` 钉住整次解析。`.python-version` 写的是 Python 3.12。机器上没有这个解释器时，uv 会装上。

这组直接依赖在 2026-11-05 的 Python 3.12 上装通过了。Hive 加载另外钉了 pyarrow 26.0.1。

| 包 | 版本 |
| --- | --- |
| tensorflow | 2.21.0 |
| keras | 3.15.1 |
| pandas | 3.1.1 |
| numpy | 2.5.4 |
| scikit-learn | 1.9.1 |
| minisom | 2.3.6 |
| matplotlib | 3.11.2 |
| seaborn | 0.13.2 |
| pyarrow | 26.0.1 |

Keras 单独钉住。TensorFlow 2.21.0 只要求 `keras>=3.12`。版本钉死之后，一次新安装会停在这组数字上，pandas 停在 3.1.1，numpy 停在 2.5.4。K-Means 把 `n_init` 设成 10。scikit-learn 1.4 把默认值改成了 `auto`。

GitHub Actions 怎么跑这些版本，写在 [CI 和项目站点](ci.zh-CN.md)。训练打出什么，写在 [训练和回测](training.zh-CN.md)。

## 测试

```bash
uv run python -m unittest discover -s tests -t . -v
```

加载、标签、切分、回测这几项测试用 pandas 和 sklearn。机器上有 TensorFlow 时，`tests/test_model.py` 会建混合专家，并跑 `main(epochs=1)`。没有 TensorFlow 时，这几项跳过。

Hive 聚合那项检查用 pandas 和 pyarrow。

```bash
uv run python -m unittest tests.test_hive_daily_bars
```

这个检查和目录结构一起写在 [数据](data.zh-CN.md)。
