# 策略文件映射关系文档

## 概述
本文档说明6个交易策略与实际JSONL文件的对应关系，以及它们的存储位置。

## 策略列表与文件映射

### 1. 见顶信号+涨幅前8做空
- **策略Key**: `top_signal_top8_short`
- **文件格式**: `{account_id}_top_signal_top8_short_execution.jsonl`
- **存储目录**: `data/okx_auto_strategy/`
- **示例文件**: `account_main_top_signal_top8_short_execution.jsonl`
- **strategy_type字段**: `"top8_short"`

### 2. 见顶信号+涨幅后8做空
- **策略Key**: `top_signal_bottom8_short`
- **文件格式**: `{account_id}_top_signal_bottom8_short_execution.jsonl`
- **存储目录**: `data/okx_auto_strategy/`
- **示例文件**: `account_main_top_signal_bottom8_short_execution.jsonl`
- **strategy_type字段**: `"bottom8_short"`

### 3. 见底信号+涨幅前8做多
- **策略Key**: `bottom_signal_top8_long`
- **文件格式**: `{account_id}_bottom_signal_top8_long_execution.jsonl`
- **存储目录**: `data/okx_bottom_signal_execution/` ⚠️ 注意不同的目录！
- **示例文件**: `account_main_bottom_signal_top8_long_execution.jsonl`
- **strategy_type字段**: `"top8_long"`

### 4. 见底信号+涨幅后8做多
- **策略Key**: `bottom_signal_bottom8_long`
- **文件格式**: `{account_id}_bottom_signal_bottom8_long_execution.jsonl`
- **存储目录**: `data/okx_bottom_signal_execution/` ⚠️ 注意不同的目录！
- **示例文件**: `account_main_bottom_signal_bottom8_long_execution.jsonl`
- **strategy_type字段**: `"bottom8_long"`

### 5. BTC触发涨幅后8名(抄底)
- **策略Key**: `btc_bottom8_copy`
- **文件格式**: `{account_id}_btc_bottom_performers_execution.jsonl`
- **存储目录**: `data/okx_auto_strategy/`
- **示例文件**: `account_main_btc_bottom_performers_execution.jsonl`
- **strategy_type字段**: `"bottom_performers"`

### 6. BTC触发涨幅前8名(追涨)
- **策略Key**: `btc_top8_chase`
- **文件格式**: `{account_id}_btc_top_performers_execution.jsonl`
- **存储目录**: `data/okx_auto_strategy/`
- **示例文件**: `account_main_btc_top_performers_execution.jsonl`
- **strategy_type字段**: `"top_performers"`

## 文件结构示例

每个策略文件的第一行是JSON格式的配置记录：

```json
{
  "timestamp": "2026-02-21T12:53:42.922363",
  "time": "2026-02-21 12:53:42",
  "account_id": "account_main",
  "strategy_type": "top8_long",
  "allowed": true,
  "reason": "测试重置功能",
  "rsi_value": 0,
  "sentiment": "--"
}
```

### 关键字段说明

- **allowed**: `true` = 策略开启，`false` = 策略关闭
- **timestamp**: 最后更新时间（ISO 8601格式）
- **strategy_type**: 策略类型标识
- **reason**: 开启/关闭原因说明
- **rsi_value**: RSI阈值（如果适用）
- **sentiment**: 市场情绪（如果适用）

## 账户列表

系统支持4个交易账户：

1. **account_main** - 主账户
2. **account_fangfang12** - fangfang12账户
3. **account_anchor** - 锚点账户
4. **account_poit_main** - POIT子账户

## API查询方式

### 获取所有账户策略状态
```bash
GET /api/order-scheduler/account-strategies
```

返回示例：
```json
{
  "success": true,
  "accounts": [
    {
      "account_id": "account_main",
      "account_name": "主账户",
      "strategies": [
        {
          "key": "top_signal_top8_short",
          "name": "见顶信号+涨幅前8做空",
          "enabled": true,
          "last_update": "2026-02-21T11:59:06.232170"
        },
        ...
      ]
    },
    ...
  ]
}
```

## 目录结构

```
/home/user/webapp/data/
├── okx_auto_strategy/
│   ├── account_main_top_signal_top8_short_execution.jsonl
│   ├── account_main_top_signal_bottom8_short_execution.jsonl
│   ├── account_main_btc_bottom_performers_execution.jsonl
│   ├── account_main_btc_top_performers_execution.jsonl
│   └── ... (其他账户的文件)
│
└── okx_bottom_signal_execution/
    ├── account_main_bottom_signal_top8_long_execution.jsonl
    ├── account_main_bottom_signal_bottom8_long_execution.jsonl
    └── ... (其他账户的文件)
```

## 注意事项

1. **目录差异**: 见底信号策略（策略3和4）存储在独立的 `okx_bottom_signal_execution/` 目录中
2. **文件命名**: 所有文件遵循 `{account_id}_{strategy_pattern}_execution.jsonl` 格式
3. **只读第一行**: API只读取每个文件的第一行来获取当前状态
4. **绝对路径**: API使用绝对路径 `/home/user/webapp/data` 来确保正确访问
5. **未配置策略**: 如果文件不存在，策略状态显示为 `enabled: false, last_update: null`

## 故障排查

### 策略状态显示不正确

1. 检查文件是否存在：
```bash
ls -la /home/user/webapp/data/okx_auto_strategy/account_main_*.jsonl
ls -la /home/user/webapp/data/okx_bottom_signal_execution/account_main_*.jsonl
```

2. 检查文件内容：
```bash
cat /home/user/webapp/data/okx_bottom_signal_execution/account_main_bottom_signal_top8_long_execution.jsonl
```

3. 验证JSON格式：
```bash
head -n1 /home/user/webapp/data/okx_bottom_signal_execution/account_main_bottom_signal_top8_long_execution.jsonl | jq .
```

### API返回错误

1. 检查Flask应用日志：
```bash
pm2 logs flask-app --nostream --lines 50
```

2. 测试API直接访问：
```bash
curl -s http://localhost:9002/api/order-scheduler/account-strategies | jq .
```

## 更新历史

- **2026-02-21**: 修复API绝对路径问题，确保正确读取见底信号策略
- **2026-02-21**: 创建策略文件映射文档

---

**访问地址**: https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/order-scheduler
