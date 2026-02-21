# 见底信号做多策略功能说明

## 📈 功能概述

新增两个做多策略，用于在市场见底时自动开仓：
1. **见底信号+涨幅前8做多**：对涨幅前8名币种开多单
2. **见底信号+涨幅后8做多**：对涨幅后8名币种开多单

## 🎯 触发条件

### 必须同时满足以下所有条件：
1. **市场情绪信号**
   - 出现「✅见底信号」或
   - 出现「📉底部背离」

2. **RSI指标**
   - RSI总和 < 阈值（默认800）
   - 阈值可手动设置（范围：300-1500）

3. **币种选择**
   - 从15个常用币中选择
   - 涨幅前8策略：选择涨幅最高的8个
   - 涨幅后8策略：选择涨幅最低的8个

## 💰 交易参数

### 资金配置
- **总投入**：可用余额的 **1.5%**
- **分配方式**：平均分配给8个币种
- **单币限额**：默认最高 **5.0 USDT**（可手动设置，范围：1-100）

### 交易设置
- **杠杆倍数**：10倍
- **开仓方向**：做多（Long）
- **持仓管理**：与现有止盈止损系统配合

## ⚙️ 策略配置

### 可配置参数

1. **策略开关**
   - 开启/关闭策略监控
   - 每个账户独立配置

2. **RSI阈值**
   - 默认值：800
   - 调整范围：300-1500
   - 点击✏️图标编辑

3. **单币限额**
   - 默认值：5.0 USDT
   - 调整范围：1-100 USDT
   - 点击✏️图标编辑

### 配置保存
- 自动保存到服务器
- 按账户独立存储
- 记录到策略日志

## 🔄 执行机制

### 监控频率
- **检查间隔**：每60秒检查一次市场条件
- **冷却时间**：触发后1小时内不重复执行
- **并发控制**：同一账户同一策略类型的执行许可管理

### 执行流程
1. 定时检查市场情绪和RSI指标
2. 满足触发条件时，读取JSONL执行许可文件
3. 如果允许执行（allowed=true），则执行策略：
   - 获取当前币种涨幅数据
   - 选择前8或后8名币种
   - 计算每个币种的开仓金额
   - 执行开仓操作
   - 记录到策略日志
4. 执行完成后，将执行许可设为false
5. 1小时冷却期后，可手动或自动重置执行许可

## 📊 UI展示

### 策略卡片颜色
- **涨幅前8做多**：绿色主题 (#22c55e)
- **涨幅后8做多**：深绿色主题 (#10b981)

### 实时信息显示
- 当前市场情绪
- 当前RSI总和
- 最后更新时间
- RSI阈值（可编辑）
- 单币限额（可编辑）

### 操作按钮
- 开关按钮：开启/关闭策略
- 编辑按钮：修改RSI阈值和单币限额
- 刷新按钮：刷新账户信息

## 🔐 数据存储

### 配置文件路径
```
data/okx_bottom_signal_long/{account_id}_top8_long_config.json
data/okx_bottom_signal_long/{account_id}_bottom8_long_config.json
```

### 配置文件结构
```json
{
  "enabled": true,
  "rsi_threshold": 800,
  "max_order_size": 5.0,
  "position_size_percent": 1.5,
  "leverage": 10,
  "last_updated": "2026-02-21T12:00:00Z"
}
```

### 执行许可文件路径
```
data/okx_auto_strategy/{account_id}_bottom_signal_top8_long_execution.jsonl
data/okx_auto_strategy/{account_id}_bottom_signal_bottom8_long_execution.jsonl
```

### 执行许可文件格式（JSONL，首行为头记录）
```json
{"timestamp": "2026-02-21T12:00:00", "account_id": "account_main", "strategy_type": "top8_long", "allowed": true, "reason": "开启见底信号+涨幅前8做多监控", "rsi_value": 750, "sentiment": "✅见底信号"}
{"timestamp": "2026-02-21T12:05:00", "execution_time": "2026-02-21T12:05:00", "allowed": false, "reason": "策略已执行", "total_amount": 15.0, "position_count": 8}
```

## 📝 策略日志

### 日志类型
1. **配置变更日志**
   - 策略开关变更
   - RSI阈值修改
   - 单币限额调整

2. **开仓日志**
   - 触发条件
   - 开仓币种
   - 开仓金额
   - 执行结果

### 日志存储
- 路径：`data/okx_strategy_logs/strategy_log_{account_id}_{date}.jsonl`
- 格式：JSONL
- 防篡改：SHA-256哈希校验

## 🔌 API端点

### 1. 配置管理（涨幅前8）
```
GET  /api/okx-trading/bottom-signal-long-top8/<account_id>
POST /api/okx-trading/bottom-signal-long-top8/<account_id>
```

### 2. 配置管理（涨幅后8）
```
GET  /api/okx-trading/bottom-signal-long-bottom8/<account_id>
POST /api/okx-trading/bottom-signal-long-bottom8/<account_id>
```

### 3. 执行许可管理
```
GET  /api/okx-trading/check-bottom-signal-allowed/<account_id>/<strategy_type>
POST /api/okx-trading/set-allowed-bottom-signal/<account_id>/<strategy_type>
```

参数：
- `account_id`: 账户ID（如：account_main）
- `strategy_type`: 策略类型（top8_long 或 bottom8_long）

### 请求示例
```bash
# 保存配置
curl -X POST http://localhost:9002/api/okx-trading/bottom-signal-long-top8/account_main \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "rsi_threshold": 800,
    "max_order_size": 5.0,
    "position_size_percent": 1.5,
    "leverage": 10
  }'

# 设置执行许可
curl -X POST http://localhost:9002/api/okx-trading/set-allowed-bottom-signal/account_main/top8_long \
  -H "Content-Type: application/json" \
  -d '{
    "allowed": true,
    "reason": "手动重置执行许可",
    "rsiValue": 750,
    "sentiment": "✅见底信号"
  }'
```

## 🎨 前端代码

### JavaScript函数
- `saveBottomSignalTop8Config()` - 保存涨幅前8策略配置
- `saveBottomSignalBottom8Config()` - 保存涨幅后8策略配置
- `loadBottomSignalTop8Config()` - 加载涨幅前8策略配置
- `loadBottomSignalBottom8Config()` - 加载涨幅后8策略配置

### CSS类
- `.slider-bottom-signal-top8-long` - 涨幅前8开关样式
- `.slider-bottom-signal-bottom8-long` - 涨幅后8开关样式

## 📌 使用说明

### 首次使用

1. **选择账户**
   - 在页面左侧"账户管理"区域选择或添加账户

2. **配置策略**
   - 滚动到"见底信号+涨幅前8做多"或"见底信号+涨幅后8做多"卡片
   - 根据需要调整RSI阈值（点击✏️图标）
   - 根据需要调整单币限额（点击✏️图标）

3. **开启策略**
   - 点击开关按钮
   - 系统会显示确认提示，包含所有配置信息
   - 确认后策略开始监控

4. **查看日志**
   - 在"📊 策略执行日志"区域查看策略执行记录
   - 点击日志条目展开查看详情

### 日常使用

1. **监控市场状态**
   - 实时查看"当前市场情绪"和"当前RSI总和"
   - 绿色表示可能触发做多

2. **调整参数**
   - 根据市场情况随时调整RSI阈值
   - 根据资金情况调整单币限额
   - 修改后自动保存并记录到日志

3. **查看执行结果**
   - 策略触发后在"策略执行日志"中查看
   - 查看开仓币种、金额、价格等详情

## ⚠️ 注意事项

### 风险提示
1. **市场风险**
   - 见底信号不一定准确，可能出现假信号
   - 建议配合其他指标综合判断
   - 注意控制总体仓位

2. **资金管理**
   - 单次投入为可用余额的1.5%
   - 8个币种平均分配
   - 单币有最高限额保护

3. **杠杆风险**
   - 10倍杠杆放大收益的同时也放大风险
   - 建议设置好止损保护
   - 密切关注持仓情况

### 使用建议
1. **初始设置**
   - 建议从较低的RSI阈值开始（如600-700）
   - 观察一段时间后再调整
   - 先用小额测试

2. **配合止盈止损**
   - 开启普通止盈止损
   - 开启RSI多单止盈
   - 开启市场情绪止盈

3. **定期检查**
   - 每天查看策略执行日志
   - 定期评估策略效果
   - 根据市场情况调整参数

## 🔧 维护信息

### 文件位置
- **前端**：`templates/okx_trading.html`
- **后端**：`app.py`
- **配置目录**：`data/okx_bottom_signal_long/`
- **执行许可**：`data/okx_auto_strategy/`
- **日志目录**：`data/okx_strategy_logs/`

### 代码统计
- 前端代码：521行（HTML + JavaScript + CSS）
- 后端代码：301行（4个API端点）
- 总计：822行

### 版本信息
- 功能版本：v1.0
- 添加日期：2026-02-21
- Git提交：c96365b

## 📞 技术支持

如有问题，请查看：
- 策略执行日志：查看详细的执行记录
- Flask日志：`pm2 logs flask-app`
- 浏览器控制台：查看JavaScript错误

---

**页面访问地址**：
https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/okx-trading

**建议**：滚动到"见底信号+涨幅前8做多"和"见底信号+涨幅后8做多"卡片区域进行配置和使用。
