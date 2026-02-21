# 系统日志按日期保存机制

**日期**: 2026-02-21  
**版本**: v2.7.2  
**状态**: ✅ 已实现  

---

## 📋 概述

系统中的所有日志文件现在都按日期保存，每天一个JSONL文件。这样可以：
- 方便按日期查询历史记录
- 避免单个文件过大
- 便于日志归档和清理
- 提高查询性能

---

## 📂 日志文件结构

### 1. 订单调度中心日志

**目录**: `data/order_scheduler_logs/`

**文件格式**:
```
executions_YYYYMMDD.jsonl     # 订单执行日志（按日期）
scheduler_YYYYMMDD.log        # 调度器运行日志（按日期）
```

**示例**:
```
data/order_scheduler_logs/
├── executions_20260221.jsonl  # 2026年2月21日的订单执行日志
├── executions_20260220.jsonl  # 2026年2月20日的订单执行日志
├── scheduler_20260221.log     # 2026年2月21日的调度器日志
└── scheduler_20260220.log     # 2026年2月20日的调度器日志
```

**日志内容示例** (`executions_20260221.jsonl`):
```json
{"request_id": "account_main_1708531200000", "timestamp": "2026-02-21T10:30:00", "account_id": "account_main", "symbol": "BTC/USDT:USDT", "side": "buy", "order_type": "market", "amount": 0.001, "price": null, "leverage": 10, "strategy_name": "bottom_signal_long", "status": "success", "order_id": "123456789", "metadata": {}}
{"request_id": "account_poit_main_1708531260000", "timestamp": "2026-02-21T10:31:00", "account_id": "account_poit_main", "symbol": "ETH/USDT:USDT", "side": "buy", "order_type": "market", "amount": 0.01, "price": null, "leverage": 10, "strategy_name": "bottom_signal_long", "status": "success", "order_id": "123456790", "metadata": {}}
```

---

### 2. 见底信号做多策略执行日志

**目录**: `data/okx_auto_strategy/`

**文件格式**:
```
{account_id}_bottom_signal_{strategy_type}_execution_YYYYMMDD.jsonl
```

**参数说明**:
- `account_id`: 账户ID（如`account_main`、`account_poit_main`等）
- `strategy_type`: 策略类型（`top8_long`涨幅前8做多、`bottom8_long`涨幅后8做多）
- `YYYYMMDD`: 日期（如`20260221`）

**示例**:
```
data/okx_auto_strategy/
├── account_main_bottom_signal_top8_long_execution_20260221.jsonl
├── account_main_bottom_signal_bottom8_long_execution_20260221.jsonl
├── account_poit_main_bottom_signal_top8_long_execution_20260221.jsonl
├── account_poit_main_bottom_signal_bottom8_long_execution_20260221.jsonl
├── account_main_bottom_signal_top8_long_execution_20260220.jsonl     # 昨天的日志
└── account_main_bottom_signal_bottom8_long_execution_20260220.jsonl  # 昨天的日志
```

**文件结构**:
- **第1行（文件头）**: 执行许可状态
- **第2行及之后**: 执行详情记录

**文件头示例**:
```json
{"timestamp": "2026-02-21T10:00:00", "time": "2026-02-21 10:00:00", "account_id": "account_main", "strategy_type": "top8_long", "allowed": true, "reason": "Switch enabled", "rsi_value": 750, "sentiment": "见底信号", "date": "20260221"}
```

**执行记录示例**:
```json
{"timestamp": "2026-02-21T10:30:00", "account_id": "account_main", "strategy_key": "top8_long", "coins": ["BTC", "ETH", "SOL"], "total_amount": 15.0, "amount_per_coin": 5.0, "success_count": 3, "failed_count": 0, "success_coins": ["BTC", "ETH", "SOL"], "failed_coins": []}
```

---

## 🔍 日志查询逻辑

### 1. 订单调度中心查询

#### 查询今日和昨日数据
```python
from datetime import datetime, timedelta

# 今天
today = datetime.now().strftime('%Y%m%d')
today_file = f"data/order_scheduler_logs/executions_{today}.jsonl"

# 昨天
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
yesterday_file = f"data/order_scheduler_logs/executions_{yesterday}.jsonl"
```

#### API实现
- `get_order_history()`: 读取今天和昨天的日志
- `get_statistics()`: 统计今天和昨天的数据

---

### 2. 见底信号策略查询

#### 智能查找逻辑

**读取执行许可状态时**:
1. 优先查找今天的文件
2. 如果今天文件不存在，查找最近3天的文件
3. 如果都不存在，返回默认允许（首次执行）

**示例代码** (`bottom_signal_long_monitor.py`):
```python
def get_latest_execution_file(account_id, strategy_key):
    """获取最新的执行文件"""
    # 查找最近3天的文件
    for days_ago in range(3):
        date = datetime.now() - timedelta(days=days_ago)
        date_str = date.strftime('%Y%m%d')
        filename = f"{account_id}_bottom_signal_{strategy_key}_execution_{date_str}.jsonl"
        file_path = DATA_DIR / filename
        if file_path.exists():
            return file_path
    return None
```

**写入执行记录时**:
- 始终写入今天的文件
- 如果文件不存在则创建
- 追加模式写入

---

## 📊 API接口更新

### 1. 检查执行许可API

**端点**: `GET /api/okx-trading/check-bottom-signal-allowed/<account_id>/<strategy_type>`

**更新内容**:
- 优先读取今日文件
- 如不存在则查找最近3天的历史文件
- 返回信息包含文件来源

**响应示例**:
```json
{
  "success": true,
  "allowed": true,
  "reason": "Read from today's JSONL header",
  "lastRecord": {
    "timestamp": "2026-02-21T10:00:00",
    "account_id": "account_main",
    "strategy_type": "top8_long",
    "allowed": true,
    "date": "20260221"
  }
}
```

如果读取历史文件:
```json
{
  "success": true,
  "allowed": false,
  "reason": "Read from history file (account_main_bottom_signal_top8_long_execution_20260220.jsonl)",
  "lastRecord": {...}
}
```

---

### 2. 设置执行许可API

**端点**: `POST /api/okx-trading/set-allowed-bottom-signal/<account_id>/<strategy_type>`

**更新内容**:
- 写入今日文件
- 文件头增加`date`字段

**请求体**:
```json
{
  "allowed": true,
  "reason": "Switch enabled",
  "rsiValue": 750,
  "sentiment": "见底信号"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Execution allowed status updated successfully for 20260221",
  "header_record": {
    "timestamp": "2026-02-21T10:00:00",
    "time": "2026-02-21 10:00:00",
    "account_id": "account_main",
    "strategy_type": "top8_long",
    "allowed": true,
    "reason": "Switch enabled",
    "rsi_value": 750,
    "sentiment": "见底信号",
    "date": "20260221"
  }
}
```

---

## 🛠️ 实现细节

### 1. 文件命名规则

所有日志文件名都包含日期后缀：
```
{prefix}_{YYYYMMDD}.{extension}
```

**示例**:
- `executions_20260221.jsonl`
- `scheduler_20260221.log`
- `account_main_bottom_signal_top8_long_execution_20260221.jsonl`

---

### 2. 日期格式

统一使用 `YYYYMMDD` 格式：
```python
date_str = datetime.now().strftime('%Y%m%d')
```

**优点**:
- 易于排序
- 便于文件名匹配
- 符合国际标准

---

### 3. 历史文件查找

**向后查找3天**:
```python
from datetime import datetime, timedelta

for days_ago in range(3):  # 今天、昨天、前天
    date = datetime.now() - timedelta(days=days_ago)
    date_str = date.strftime('%Y%m%d')
    filename = f"prefix_{date_str}.jsonl"
    if os.path.exists(filename):
        return filename
```

---

### 4. 文件创建时机

**订单调度中心**:
- 每次执行订单时自动创建当天文件
- 追加模式写入

**见底信号策略**:
- 开启策略开关时创建今日文件
- 执行策略时追加记录

---

## 📌 兼容性处理

### 旧格式文件迁移

如果存在旧格式的文件（不带日期后缀），系统会：
1. 继续查找旧文件作为历史数据
2. 新数据写入带日期的文件
3. 建议手动清理或归档旧文件

**旧文件路径** (已废弃):
```
data/okx_bottom_signal_long_execution/
└── account_main_bottom_signal_top8_long_execution.jsonl  # 旧格式
```

**新文件路径**:
```
data/okx_auto_strategy/
├── account_main_bottom_signal_top8_long_execution_20260221.jsonl  # 新格式
├── account_main_bottom_signal_top8_long_execution_20260220.jsonl
└── account_main_bottom_signal_top8_long_execution_20260219.jsonl
```

---

## 🧹 日志清理建议

### 1. 保留策略

建议保留时长：
- **订单执行日志**: 保留30天
- **见底信号执行日志**: 保留30天
- **调度器运行日志**: 保留7天

---

### 2. 清理脚本

**手动清理** (删除30天前的日志):
```bash
# 进入日志目录
cd /home/user/webapp/data/order_scheduler_logs

# 删除30天前的文件
find . -name "executions_*.jsonl" -mtime +30 -delete
find . -name "scheduler_*.log" -mtime +30 -delete
```

**自动清理** (添加到crontab):
```bash
# 每天凌晨2点清理日志
0 2 * * * find /home/user/webapp/data/order_scheduler_logs -name "*.jsonl" -mtime +30 -delete
0 2 * * * find /home/user/webapp/data/order_scheduler_logs -name "*.log" -mtime +7 -delete
0 2 * * * find /home/user/webapp/data/okx_auto_strategy -name "*_execution_*.jsonl" -mtime +30 -delete
```

---

### 3. 归档脚本

**压缩旧日志**:
```bash
#!/bin/bash
# 归档7天前的日志

cd /home/user/webapp/data/order_scheduler_logs

# 获取7天前的日期
archive_date=$(date -d '7 days ago' +%Y%m%d)

# 压缩7天前的文件
tar -czf archive_${archive_date}.tar.gz executions_${archive_date}.jsonl scheduler_${archive_date}.log

# 删除原文件
rm -f executions_${archive_date}.jsonl scheduler_${archive_date}.log

echo "✅ 归档完成: archive_${archive_date}.tar.gz"
```

---

## 📈 性能优化

### 1. 文件大小控制

**按日期分文件的优点**:
- 单个文件不会无限增长
- 查询性能稳定
- 便于并行处理

**预估文件大小**:
- 假设每天执行100笔订单
- 每条记录约300字节
- 每天文件大小约30KB
- 一个月文件总大小约900KB

---

### 2. 查询优化

**只查询必要的文件**:
```python
# 只查询今天和昨天的数据
today = datetime.now().strftime('%Y%m%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

files_to_read = [
    f"executions_{today}.jsonl",
    f"executions_{yesterday}.jsonl"
]
```

**避免全目录扫描**:
```python
# ❌ 不推荐
for file in os.listdir(log_dir):
    if file.startswith('executions_'):
        # 读取所有文件

# ✅ 推荐
specific_file = f"executions_{today}.jsonl"
if os.path.exists(specific_file):
    # 只读取需要的文件
```

---

## 🔧 故障排查

### 问题1: 找不到今天的日志文件

**可能原因**:
- 今天还没有执行过订单
- 文件被误删
- 日期格式不匹配

**解决方案**:
```bash
# 检查日期格式
date +%Y%m%d

# 查看最近的日志文件
ls -lt data/order_scheduler_logs/ | head -10

# 查看Python生成的日期
python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d'))"
```

---

### 问题2: 文件权限问题

**错误信息**:
```
PermissionError: [Errno 13] Permission denied: 'executions_20260221.jsonl'
```

**解决方案**:
```bash
# 检查文件权限
ls -l data/order_scheduler_logs/

# 修改权限
chmod 644 data/order_scheduler_logs/*.jsonl
chmod 644 data/okx_auto_strategy/*.jsonl

# 修改所有者
chown user:user data/order_scheduler_logs/*.jsonl
```

---

### 问题3: 磁盘空间不足

**检查磁盘使用**:
```bash
# 查看目录大小
du -sh data/order_scheduler_logs/
du -sh data/okx_auto_strategy/

# 查看磁盘空间
df -h /home/user/webapp
```

**清理方案**:
```bash
# 压缩旧日志
cd data/order_scheduler_logs
tar -czf old_logs_$(date +%Y%m).tar.gz executions_202602*.jsonl
rm -f executions_202602*.jsonl
```

---

## ✅ 验证测试

### 1. 测试日志创建

```bash
# 检查今天的订单调度中心日志
ls -lh data/order_scheduler_logs/executions_$(date +%Y%m%d).jsonl

# 检查今天的见底信号日志
ls -lh data/okx_auto_strategy/*_$(date +%Y%m%d).jsonl
```

---

### 2. 测试API读取

```bash
# 测试调度中心状态API
curl http://localhost:9002/api/order-scheduler/status | jq

# 测试见底信号许可API
curl http://localhost:9002/api/okx-trading/check-bottom-signal-allowed/account_main/top8_long | jq
```

---

### 3. 测试历史查询

```bash
# 查看订单历史
curl "http://localhost:9002/api/order-scheduler/orders?limit=10" | jq

# 查看统计信息
curl http://localhost:9002/api/order-scheduler/stats | jq
```

---

## 📝 总结

### 主要改进

1. ✅ **订单调度中心日志按日期保存**
   - `executions_YYYYMMDD.jsonl`
   - `scheduler_YYYYMMDD.log`

2. ✅ **见底信号策略日志按日期保存**
   - `{account_id}_bottom_signal_{strategy_type}_execution_YYYYMMDD.jsonl`
   - 智能查找最近3天的历史文件

3. ✅ **API接口支持按日期查询**
   - 优先读取今日文件
   - 自动回退到历史文件
   - 返回信息包含文件来源

4. ✅ **性能优化**
   - 避免单文件过大
   - 提高查询效率
   - 便于归档清理

---

### 文件清单

**修改的文件**:
1. `source_code/order_scheduler.py` - 已按日期保存（无需修改）
2. `source_code/bottom_signal_long_monitor.py` - 更新为按日期保存
3. `app.py` - 更新API支持按日期查询

**新增功能**:
- 智能历史文件查找
- 日期后缀文件名格式
- API响应包含文件来源信息

---

**文档版本**: v1.0  
**最后更新**: 2026-02-21 16:30 UTC  
**作者**: GenSpark AI Developer  
**状态**: ✅ 已实现并部署
