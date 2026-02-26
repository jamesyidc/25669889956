# 策略更新实施计划

## 📋 任务概述

### 删除
- ❌ 上涨占比0-涨幅前8名策略
- ❌ 上涨占比0-涨幅后8名策略

### 新增
- ✅ 见底信号+涨幅前8做多策略
- ✅ 见底信号+涨幅后8做多策略

## 🎯 新策略特性

### 触发条件
1. 市场情绪出现"见底信号"或"底部背离"
2. RSI总和 < 阈值（默认800，可手动设置）

### 交易参数
- 杠杆：10倍
- 方向：做多（long）
- 币种范围：常用币15个
- 选择逻辑：
  - 策略1：涨幅前8（跌得最少/涨得最多的8个）
  - 策略2：涨幅后8（跌得最多的8个）
- 仓位大小：可用余额 × 1.5%
- 单币限额：默认5U（可手动设置）

### 配置特性
- 每个账户独立配置
- 独立的JSONL文件存储
- 独立的开关控制
- RSI阈值可调整
- 单币限额可调整

## 📝 需要修改的部分

### 1. 版本说明（HTML注释）
位置：文件开头
- 更新版本号：v2.6.7 → v2.6.8
- 添加新策略说明

### 2. UI卡片（需要找到并替换）
删除：
- 上涨占比0-涨幅前8名卡片
- 上涨占比0-涨幅后8名卡片

添加：
- 见底信号+涨幅前8做多卡片
- 见底信号+涨幅后8做多卡片

### 3. JavaScript代码
删除：
- `checkUpRatio0Strategy()` 函数
- 上涨占比0相关的事件监听
- 上涨占比0相关的配置加载/保存

添加：
- `checkBottomSignalTop8Long()` 函数
- `checkBottomSignalBottom8Long()` 函数
- 配置保存/加载逻辑
- JSONL执行许可检查

### 4. 后端API（app.py）
添加：
- `/api/okx-trading/bottom-signal-long-top8/<account>` (GET/POST)
- `/api/okx-trading/bottom-signal-long-bottom8/<account>` (GET/POST)
- `/api/okx-trading/check-bottom-signal-allowed/<account>/<strategy_type>` (GET)
- `/api/okx-trading/update-bottom-signal-execution/<account>/<strategy_type>` (POST)

### 5. 策略执行逻辑
- 检测见底信号（从市场情绪API获取）
- 验证RSI阈值
- 获取常用币15个的涨跌幅数据
- 排序并选择前8或后8
- 执行开仓（10倍杠杆）
- 记录到策略日志

## 📂 文件结构

### 配置文件
```
data/okx_bottom_signal_long/
  ├── {account}_bottom_signal_top8_long.jsonl
  └── {account}_bottom_signal_bottom8_long.jsonl
```

### JSONL执行许可文件
```
data/okx_bottom_signal_long_execution/
  ├── {account}_top8_execution.jsonl
  └── {account}_bottom8_execution.jsonl
```

## 🔍 关键搜索词

在代码中需要搜索和替换：
- `上涨占比0`
- `upRatio0`
- `up_ratio_0`
- `checkUpRatio0Strategy`
