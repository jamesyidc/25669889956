# 策略状态验证报告

**验证时间**: 2026-02-21  
**验证方式**: 逐个读取24个JSONL文件的第一行并解析`allowed`字段

## ✅ 验证结果：100%准确

API返回的策略状态与实际JSONL文件内容**完全一致**。

---

## 📋 详细验证清单 (24个策略配置)

### 1️⃣ account_main (主账户)

| # | 策略名称 | 文件路径 | allowed字段 | 状态 | 最后更新 |
|---|---------|---------|-----------|------|---------|
| 1 | 见顶信号+涨幅前8做空 | `data/okx_auto_strategy/account_main_top_signal_top8_short_execution.jsonl` | `true` | ✅ 开启 | 2026-02-21 11:59:06 |
| 2 | 见顶信号+涨幅后8做空 | `data/okx_auto_strategy/account_main_top_signal_bottom8_short_execution.jsonl` | `false` | ❌ 关闭 | 2026-02-21 14:36:14 |
| 3 | 见底信号+涨幅前8做多 | `data/okx_bottom_signal_execution/account_main_bottom_signal_top8_long_execution.jsonl` | `true` | ✅ 开启 | 2026-02-21 12:53:42 |
| 4 | 见底信号+涨幅后8做多 | `data/okx_bottom_signal_execution/account_main_bottom_signal_bottom8_long_execution.jsonl` | `true` | ✅ 开启 | 2026-02-21 13:53:03 |
| 5 | BTC触发涨幅后8名(抄底) | `data/okx_auto_strategy/account_main_btc_bottom_performers_execution.jsonl` | `true` | ✅ 开启 | 2026-02-17 04:19:01 |
| 6 | BTC触发涨幅前8名(追涨) | `data/okx_auto_strategy/account_main_btc_top_performers_execution.jsonl` | `true` | ✅ 开启 | 2026-02-18 01:58:42 |

**汇总**: 5个开启，1个关闭

---

### 2️⃣ account_fangfang12

| # | 策略名称 | 文件路径 | allowed字段 | 状态 | 最后更新 |
|---|---------|---------|-----------|------|---------|
| 1 | 见顶信号+涨幅前8做空 | `data/okx_auto_strategy/account_fangfang12_top_signal_top8_short_execution.jsonl` | `true` | ✅ 开启 | 2026-02-20 15:30:23 |
| 2 | 见顶信号+涨幅后8做空 | `data/okx_auto_strategy/account_fangfang12_top_signal_bottom8_short_execution.jsonl` | `true` | ✅ 开启 | 2026-02-20 15:30:23 |
| 3 | 见底信号+涨幅前8做多 | `data/okx_bottom_signal_execution/account_fangfang12_bottom_signal_top8_long_execution.jsonl` | `true` | ✅ 开启 | 2026-02-21 13:53:03 |
| 4 | 见底信号+涨幅后8做多 | `data/okx_bottom_signal_execution/account_fangfang12_bottom_signal_bottom8_long_execution.jsonl` | `true` | ✅ 开启 | 2026-02-21 13:53:03 |
| 5 | BTC触发涨幅后8名(抄底) | `data/okx_auto_strategy/account_fangfang12_btc_bottom_performers_execution.jsonl` | `true` | ✅ 开启 | 2026-02-17 04:18:35 |
| 6 | BTC触发涨幅前8名(追涨) | `data/okx_auto_strategy/account_fangfang12_btc_top_performers_execution.jsonl` | *文件不存在* | ⚪ 未配置 | - |

**汇总**: 5个开启，1个未配置

---

### 3️⃣ account_anchor (锚点账户)

| # | 策略名称 | 文件路径 | allowed字段 | 状态 | 最后更新 |
|---|---------|---------|-----------|------|---------|
| 1 | 见顶信号+涨幅前8做空 | `data/okx_auto_strategy/account_anchor_top_signal_top8_short_execution.jsonl` | `true` | ✅ 开启 | 2026-02-20 15:30:23 |
| 2 | 见顶信号+涨幅后8做空 | `data/okx_auto_strategy/account_anchor_top_signal_bottom8_short_execution.jsonl` | `true` | ✅ 开启 | 2026-02-20 15:30:23 |
| 3 | 见底信号+涨幅前8做多 | `data/okx_bottom_signal_execution/account_anchor_bottom_signal_top8_long_execution.jsonl` | `true` | ✅ 开启 | 2026-02-21 13:53:03 |
| 4 | 见底信号+涨幅后8做多 | `data/okx_bottom_signal_execution/account_anchor_bottom_signal_bottom8_long_execution.jsonl` | `true` | ✅ 开启 | 2026-02-21 13:53:03 |
| 5 | BTC触发涨幅后8名(抄底) | `data/okx_auto_strategy/account_anchor_btc_bottom_performers_execution.jsonl` | *文件不存在* | ⚪ 未配置 | - |
| 6 | BTC触发涨幅前8名(追涨) | `data/okx_auto_strategy/account_anchor_btc_top_performers_execution.jsonl` | *文件不存在* | ⚪ 未配置 | - |

**汇总**: 4个开启，2个未配置

---

### 4️⃣ account_poit_main (POIT子账户)

| # | 策略名称 | 文件路径 | allowed字段 | 状态 | 最后更新 |
|---|---------|---------|-----------|------|---------|
| 1 | 见顶信号+涨幅前8做空 | `data/okx_auto_strategy/account_poit_main_top_signal_top8_short_execution.jsonl` | `true` | ✅ 开启 | 2026-02-20 15:30:23 |
| 2 | 见顶信号+涨幅后8做空 | `data/okx_auto_strategy/account_poit_main_top_signal_bottom8_short_execution.jsonl` | `true` | ✅ 开启 | 2026-02-20 15:30:23 |
| 3 | 见底信号+涨幅前8做多 | `data/okx_bottom_signal_execution/account_poit_main_bottom_signal_top8_long_execution.jsonl` | `true` | ✅ 开启 | 2026-02-21 13:53:03 |
| 4 | 见底信号+涨幅后8做多 | `data/okx_bottom_signal_execution/account_poit_main_bottom_signal_bottom8_long_execution.jsonl` | `true` | ✅ 开启 | 2026-02-21 13:53:03 |
| 5 | BTC触发涨幅后8名(抄底) | `data/okx_auto_strategy/account_poit_main_btc_bottom_performers_execution.jsonl` | `true` | ✅ 开启 | 2026-02-17 04:39:35 |
| 6 | BTC触发涨幅前8名(追涨) | `data/okx_auto_strategy/account_poit_main_btc_top_performers_execution.jsonl` | `true` | ✅ 开启 | 2026-02-18 01:56:08 |

**汇总**: 全部6个策略均已开启 ✅

---

## 📊 总体统计

| 账户 | 开启策略数 | 关闭策略数 | 未配置策略数 | 总计 |
|------|-----------|-----------|-------------|------|
| account_main | 5 | 1 | 0 | 6 |
| account_fangfang12 | 5 | 0 | 1 | 6 |
| account_anchor | 4 | 0 | 2 | 6 |
| account_poit_main | 6 | 0 | 0 | 6 |
| **合计** | **20** | **1** | **3** | **24** |

---

## 🔍 API验证

```bash
# 测试命令
curl -s http://localhost:9002/api/order-scheduler/account-strategies | jq .

# 验证结果
✅ API返回的enabled字段与JSONL文件的allowed字段100%一致
✅ API返回的last_update与JSONL文件的timestamp字段100%一致
✅ 未配置的策略正确返回 enabled: false, last_update: null
```

---

## 📁 文件位置说明

### 见顶信号策略 (策略1-2)
**目录**: `data/okx_auto_strategy/`
- `{account_id}_top_signal_top8_short_execution.jsonl`
- `{account_id}_top_signal_bottom8_short_execution.jsonl`

### 见底信号策略 (策略3-4) ⚠️
**目录**: `data/okx_bottom_signal_execution/` ← 注意是不同的目录！
- `{account_id}_bottom_signal_top8_long_execution.jsonl`
- `{account_id}_bottom_signal_bottom8_long_execution.jsonl`

### BTC触发策略 (策略5-6)
**目录**: `data/okx_auto_strategy/`
- `{account_id}_btc_bottom_performers_execution.jsonl`
- `{account_id}_btc_top_performers_execution.jsonl`

---

## ✅ 验证结论

1. **数据准确性**: 100% - 所有24个策略状态均从实际JSONL文件读取
2. **API正确性**: 100% - API返回数据与文件内容完全一致
3. **前端显示**: 100% - 页面显示的状态与后端数据同步

**问题已完全解决** ✅

---

**访问地址**: https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/order-scheduler

**验证脚本**: `/tmp/check_all_strategies.sh`
