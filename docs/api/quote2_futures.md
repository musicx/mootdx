## 扩展行情接口中国期货实测

> 实测时间: 2026-04-24
>
> 测试环境:
> - Python: `E:\Code\git\stock_related_repoes\.venv\Scripts\python.exe`
> - mootdx: 当前仓库工作树
> - 扩展行情服务器: 默认 `EX` 线路

## 01. 结论

当前 `mootdx` 的扩展行情接口可以正常获取中国期货市场的以下数据:

- 实时行情: `quote()`
- 当日分时: `minute()`
- 日线 / 周线 / 月线: `bars()`
- 分钟 K 线 (`1m` / `5m` / `15m` / `ex_1m`): `bars()`

当前**不能**通过扩展行情接口获取:

- 财务 / 基本面: `finance()`
- F10: `F10()` / `F10C()`

当前**不建议依赖**:

- 历史分时: `minutes()`

实测中，`minutes()` 对中国期货合约返回空结果；历史分钟数据应改用 `bars()` 的分钟级 K 线。

## 02. 可用中国期货市场

`markets()` 返回的中国期货相关市场如下:

| 市场 ID | 名称 |
| --- | --- |
| 28 | 郑州商品 |
| 29 | 大连商品 |
| 30 | 上海期货 |
| 47 | 中金所期货 |
| 60 | 主力期货合约 |
| 66 | 广州期货 |

说明:

- `60` 会在 `markets()` 中出现，但本次实测没有在 `instrument()` 中拿到当前可用合约。
- 因此下面的日期清单使用了各交易所的主连样本合约做实测。

## 03. 字段清单

### 3.1 `quote()`

实测样例: `client.quote(47, "IF2605")`

返回字段:

`market, code, pre_close, open, high, low, price, kaicang, zongliang, xianliang, neipan, waipan, chicang, bid1, bid2, bid3, bid4, bid5, bid_vol1, bid_vol2, bid_vol3, bid_vol4, bid_vol5, ask1, ask2, ask3, ask4, ask5, ask_vol1, ask_vol2, ask_vol3, ask_vol4, ask_vol5`

### 3.2 `minute()`

实测样例: `client.minute(47, "IF2605")`

返回字段:

`hour, minute, price, avg_price, volume, open_interest`

### 3.3 `bars()`

实测样例:

- `client.bars(KLINE_DAILY, 47, "IFL8", 0, 3)`
- `client.bars(KLINE_1MIN, 47, "IF2605", 0, 3)`

返回字段:

`open, high, low, close, position, trade, price, year, month, day, hour, minute, datetime, amount`

说明:

- 日线和分钟 K 线都走 `bars()`
- `1m`、`5m`、`15m`、`ex_1m` 都可返回数据

## 04. 最早可取日期清单

下面是按中国期货市场主连样本合约做的实测结果。

这些日期表示“当前服务器上，针对该样本合约实测能回溯到的最早时间”，不是对所有合约的绝对保证下界。

| 市场 | 样本合约 | 日线最早日期 | 1 分钟 K 线最早日期 |
| --- | --- | --- | --- |
| 郑州商品 (28) | `SRL8` | `2013-08-19 15:00:00` | `2021-11-24 11:26:00` |
| 大连商品 (29) | `AL8` | `2013-08-19 15:00:00` | `2021-10-25 14:55:00` |
| 上海期货 (30) | `AUL8` | `2013-08-19 15:00:00` | `2023-07-18 11:03:00` |
| 中金所期货 (47) | `IFL8` | `2010-04-19 15:00:00` | `2019-12-27 13:41:00` |
| 广州期货 (66) | `LCL8` | `2023-07-21 15:00:00` | `2023-10-30 09:01:00` |

补充样例:

| 市场 | 样本合约 | 日线最早日期 |
| --- | --- | --- |
| 广州期货 (66) | `SIL8` | `2022-12-22 15:00:00` |
| 中金所期货 (47) | `TFL8` | `2013-09-06 15:00:00` |

## 04.1 全量主连合约扫描结果

本仓库已补充全量扫描产物:

- 明细 Markdown: `docs/api/quote2_futures_scan.md`
- 明细 CSV: `docs/api/quote2_futures_scan.csv`
- 重跑脚本: `scripts/scan_ext_futures_main_contracts.py`

本次全量扫描覆盖:

- 郑州商品: `22` 个主连合约
- 大连商品: `23` 个主连合约
- 上海期货: `25` 个主连合约
- 中金所期货: `8` 个主连合约
- 广州期货: `5` 个主连合约

按市场汇总的最早日期如下:

| 市场 | 主连数量 | 全量扫描中的最早日线日期 | 全量扫描中的最早 1 分钟 K 线日期 |
| --- | --- | --- | --- |
| 郑州商品 (28) | `22` | `2013-08-19 15:00:00` | `2016-12-26 13:31:00` |
| 大连商品 (29) | `23` | `2013-08-19 15:00:00` | `2016-12-26 13:31:00` |
| 上海期货 (30) | `25` | `2013-08-19 15:00:00` | `2016-12-26 13:31:00` |
| 中金所期货 (47) | `8` | `2010-04-19 15:00:00` | `2019-12-27 13:41:00` |
| 广州期货 (66) | `5` | `2022-12-22 15:00:00` | `2023-10-30 09:01:00` |

如果需要逐合约清单，请直接查看 `quote2_futures_scan.md` 或 `quote2_futures_scan.csv`。

## 05. Findings

### 5.1 根因

扩展行情接口此前表现为“坏掉”，根因不是 TDX 扩展协议整体失效，而是 `mootdx` 的判空重试逻辑和新版 `pandas` 不兼容:

- 原逻辑在 `check_empty()` 中对 `DataFrame` 调用 `value.all()`
- 当返回结果包含 `datetime64` 列时，`pandas 3.x` 会抛出 `TypeError`
- 这会导致诸如 `transaction()` 之类的接口在重试阶段异常退出，看起来像接口本身坏掉

### 5.2 已做修复

本次修改包含:

- 将 `check_empty()` 的 `DataFrame` 判空改为 `value.empty`
- 为模块级 `instance` 增加默认值 `None`
- 将扩展行情“已失效”的误导性运行时日志改为可用提示
- 将扩展行情文档说明改为“接口可用，但旧市场 ID / 合约样例可能过期”
- 增加回归测试 `tests/quotes/test_quotes_retry.py`

## 06. 使用指南

### 6.1 先探测市场和合约

```python
from mootdx.quotes import Quotes

client = Quotes.factory("ext")

markets = client.markets()
instruments = client.instrument(0, 1000)
```

建议先调用:

- `markets()` 获取当前市场 ID
- `instrument()` 获取当前可交易合约和主连代码

不要直接依赖旧文档里的市场 ID / 历史样例代码。

### 6.2 获取日线

```python
from mootdx.quotes import Quotes
from mootdx.consts import KLINE_DAILY

client = Quotes.factory("ext")
daily = client.bars(KLINE_DAILY, 47, "IFL8", 0, 10)
```

### 6.3 获取分钟 K 线

```python
from mootdx.quotes import Quotes
from mootdx.consts import KLINE_1MIN
from mootdx.consts import KLINE_5MIN
from mootdx.consts import KLINE_15MIN

client = Quotes.factory("ext")

k1 = client.bars(KLINE_1MIN, 47, "IF2605", 0, 200)
k5 = client.bars(KLINE_5MIN, 47, "IF2605", 0, 200)
k15 = client.bars(KLINE_15MIN, 47, "IF2605", 0, 200)
```

建议:

- 历史分钟数据统一走 `bars()`
- 不要把 `minutes()` 当成“历史分钟 K 线”接口使用

### 6.4 获取当日分时

```python
from mootdx.quotes import Quotes

client = Quotes.factory("ext")
tick_minute = client.minute(47, "IF2605")
```

### 6.5 获取实时行情

```python
from mootdx.quotes import Quotes

client = Quotes.factory("ext")
quote = client.quote(47, "IF2605")
```

### 6.6 基本面限制

扩展行情接口当前不提供:

- `finance()`
- `F10()`
- `F10C()`

如果需要 A 股财务 / 基本面，请使用标准股票市场接口，而不是扩展行情接口。

## 07. 验证记录

本次至少做了以下验证:

- `pytest tests\\quotes\\test_quotes_retry.py -q`
- 在线验证 `quote()`、`minute()`、`bars()`、`transaction()` 可返回结果
- 在线验证中国期货市场 `28 / 29 / 30 / 47 / 66`
- 在线验证 `ExtQuotes` 不提供 `finance()` / `F10()` / `F10C()`
- 在线验证 `minutes()` 对中国期货样本合约返回空

## 08. 建议

如果要基于当前接口做中国期货采集，建议按下面的组合来用:

- 市场 / 合约发现: `markets()` + `instrument()`
- 实时盘口: `quote()`
- 当日分时: `minute()`
- 日线 / 周线 / 月线 / 历史分钟 K 线: `bars()`

避免依赖:

- `minutes()` 获取历史分钟数据
- 扩展行情接口中的财务 / 基本面能力
