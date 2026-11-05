[English](setup.md) | **简体中文**

# 环境

本文与英文文档描述同一套行为，事实以英文和代码为准。

[项目说明](../README.zh-CN.md) · [数据](data.zh-CN.md) · [训练和回测](training.zh-CN.md) · [CI 和项目站点](ci.zh-CN.md)

在 Python 3.12 上核对过。先安装 [uv](https://docs.astral.sh/uv/) 0.13.7，然后在本目录执行：

```bash
uv sync
```

`uv sync` 会创建 `.venv` 并安装锁定的依赖。`pyproject.toml` 锁定直接依赖。`uv.lock` 锁定完整解析结果。本仓库是脚本，不是可安装的包。`.python-version` 指定 Python 3.12，本机没有该版本时 uv 会安装它。

直接依赖是 2026-11-05 在 Python 3.12 上能干净安装的那一组，再加上 Hive 加载用的 pyarrow 26.0.1：

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

Keras 单独锁定，是因为 TensorFlow 2.21.0 只要求 `keras>=3.12`。精确版本避免以后一次全新安装选到 pandas 4 或更新的 numpy。K-Means 显式使用 `n_init=10`，因为 scikit-learn 1.4 把默认值改成了 `auto`。

这些版本在 GitHub Actions 里怎么跑，写在 [CI 和项目站点](ci.zh-CN.md)。训练之后脚本打印什么，写在 [训练和回测](training.zh-CN.md)。

## 测试

```bash
uv run python -m unittest discover -s tests -t . -v
```

加载、标签、切分和回测不会导入 TensorFlow。安装了 TensorFlow 时，`tests/test_model.py` 会构建混合专家并执行 `main(epochs=1)`。未安装时这些测试跳过。

Hive 聚合检查不需要 TensorFlow：

```bash
uv run python -m unittest tests.test_hive_daily_bars
```

这个检查和目录结构一起写在 [数据](data.zh-CN.md)。
