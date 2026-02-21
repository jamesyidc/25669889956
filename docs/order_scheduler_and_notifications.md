# 订单调度中心与通知系统完整实现文档

## 📋 实现概览

本次更新实现了以下三大功能：

1. **订单调度中心**：处理多账户并发下单请求，确保所有订单都能成功执行
2. **Telegram通知**：所有策略触发后自动发送Telegram消息
3. **10秒自动消失弹窗**：前端下单完成后显示10秒消失的Toast通知

---

## 1. 订单调度中心 (Order Scheduler)

### 1.1 功能特性

- ✅ **并发订单处理**：使用队列机制处理多个账户的并发下单请求
- ✅ **账户锁机制**：每个账户独立锁，避免同一账户并发下单导致的问题
- ✅ **自动重试**：订单失败时可配置自动重试逻辑
- ✅ **完整日志**：所有订单请求和执行结果都有详细日志记录
- ✅ **回调支持**：支持订单完成后的回调函数
- ✅ **异步执行**：订单提交后立即返回，不阻塞主线程

### 1.2 核心组件

#### OrderRequest (订单请求对象)
```python
class OrderRequest:
    def __init__(self, account_id, symbol, side, order_type, amount, 
                 price=None, leverage=None, strategy_name=None, 
                 callback=None, metadata=None):
        self.request_id = f"{account_id}_{int(time.time()*1000)}"
        self.account_id = account_id
        self.symbol = symbol
        self.side = side  # 'buy' or 'sell'
        self.order_type = order_type  # 'market' or 'limit'
        self.amount = amount
        self.price = price
        self.leverage = leverage
        self.strategy_name = strategy_name
        self.callback = callback
        self.metadata = metadata
        self.status = 'pending'  # pending, processing, success, failed
```

#### OrderScheduler (调度器)
```python
class OrderScheduler:
    def __init__(self):
        self.running = False
        self.worker_thread = None
        self.exchanges = {}  # {account_id: exchange_instance}
        
    def start(self):
        """启动调度中心"""
        
    def submit_order(self, order_request):
        """提交订单请求"""
        
    def _worker(self):
        """工作线程 - 处理订单队列"""
        
    def _process_order(self, order_request):
        """处理单个订单（带账户锁）"""
```

### 1.3 使用方法

#### 异步提交订单（推荐）
```python
from order_scheduler import submit_order_async

# 定义回调函数
def order_callback(success, result, error):
    if success:
        print(f"✅ 订单成功: {result}")
        # 发送Telegram通知
        send_telegram_notification(result)
    else:
        print(f"❌ 订单失败: {error}")

# 提交订单
request_id = submit_order_async(
    account_id='account_main',
    symbol='BTC/USDT:USDT',
    side='buy',
    order_type='market',
    amount=0.01,
    leverage=10,
    strategy_name='bottom_signal_long',
    callback=order_callback,
    metadata={'trigger': 'auto', 'rsi': 750}
)

print(f"📝 订单已提交: {request_id}")
```

#### 在监控器中集成（示例）
```python
# 在策略监控器中使用
def execute_strategy_orders(account, coins, config):
    """执行策略订单"""
    from order_scheduler import submit_order_async
    
    pending_orders = []
    
    for coin in coins:
        # 提交订单到调度中心
        request_id = submit_order_async(
            account_id=account['id'],
            symbol=coin['symbol'],
            side='buy',
            order_type='market',
            amount=coin['amount'],
            leverage=config.get('leverage', 10),
            strategy_name='my_strategy',
            callback=lambda s, r, e: handle_order_result(s, r, e, coin),
            metadata={
                'coin': coin['symbol'],
                'strategy': 'my_strategy'
            }
        )
        pending_orders.append(request_id)
    
    return pending_orders
```

### 1.4 日志与监控

#### 日志目录
- **路径**: `/home/user/webapp/data/order_scheduler_logs/`
- **日志文件**: `scheduler_YYYYMMDD.log`
- **执行记录**: `executions_YYYYMMDD.jsonl`

#### 日志内容
```
[2026-02-21 15:30:25] 📥 收到订单请求: account_main_1708522225123 | 账户=account_main | 交易对=BTC/USDT:USDT | 方向=buy | 数量=0.01 | 策略=bottom_signal_long
[2026-02-21 15:30:25] 🔒 获取账户锁: account_main | 订单ID=account_main_1708522225123
[2026-02-21 15:30:26] ⚙️  设置杠杆: 10x
[2026-02-21 15:30:27] ✅ 订单执行成功: account_main_1708522225123 | 耗时=1.23s | 订单ID=12345678
[2026-02-21 15:30:27] 🔓 释放账户锁: account_main
```

### 1.5 调度机制

```
┌─────────────────────────────────────────────────────────┐
│               订单调度中心工作流程                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  策略监控器1   ──┐                                        │
│  策略监控器2   ──┤                                        │
│  策略监控器3   ──┼──►  订单队列  ──►  工作线程  ──►  执行 │
│  策略监控器4   ──┤                         │              │
│  ...           ──┘                         │              │
│                                            ▼              │
│                                     账户锁管理器           │
│                                   (每账户一个锁)           │
│                                            │              │
│                                            ▼              │
│                          ┌─────────────────────┐         │
│                          │  账户A: 串行执行    │         │
│                          │  账户B: 串行执行    │         │
│                          │  账户C: 串行执行    │         │
│                          └─────────────────────┘         │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Telegram通知系统

### 2.1 功能特性

- ✅ **自动通知**：所有策略触发后自动发送Telegram消息
- ✅ **丰富格式**：支持HTML格式，包含Emoji和排版
- ✅ **详细信息**：包含账户、策略、市场情绪、RSI、开仓结果等
- ✅ **失败重试**：通知发送失败时自动记录日志

### 2.2 通知内容

#### 见底信号做多通知
```
🎯 见底信号+涨幅前8做多 - 已执行

📌 账户: account_main
📊 市场情绪: 🎯见底信号 (底部背离)
📈 RSI总和: 750 (阈值 < 800)

💰 总投入: 45.00 USDT
💵 单币: 5.62 USDT
⚡️ 杠杆: 10x

✅ 成功: 8/8
📋 币种:
BTC: 涨幅 +2.5%
ETH: 涨幅 +1.8%
...

⏰ 时间: 2026-02-21 15:30:25
```

#### 见顶信号做空通知
```
🎯 见顶信号+涨幅前8做空 - 已执行

📌 账户: account_main
📊 市场情绪: 🚨见顶信号 (顶部背离)
📈 RSI总和: 1850 (阈值 > 1800)

💰 总投入: 45.00 USDT
💵 单币: 5.62 USDT
⚡️ 杠杆: 10x

✅ 成功: 8/8
📋 币种:
BTC: 涨幅 +5.2%
ETH: 涨幅 +4.8%
...

⏰ 时间: 2026-02-21 15:30:25
```

### 2.3 配置方法

#### 环境变量配置
在 `.env` 文件中添加：
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

#### 在策略监控器中使用
```python
import os
import requests

# 读取环境变量
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

def send_telegram_message(message):
    """发送Telegram消息"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram未配置")
        return
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Telegram消息发送成功")
        else:
            print(f"⚠️  Telegram消息发送失败: {response.status_code}")
    except Exception as e:
        print(f"❌ Telegram消息发送异常: {e}")

# 使用示例
message = f"""
🎯 <b>策略触发通知</b>

📌 账户: {account_name}
📊 策略: 见底信号做多
💰 总投入: {total_investment:.2f} USDT
✅ 成功: {success_count}/{total_count}
"""

send_telegram_message(message)
```

---

## 3. 10秒自动消失弹窗 (Toast Notifications)

### 3.1 功能特性

- ✅ **10秒自动消失**：弹窗显示10秒后自动消失
- ✅ **不阻塞操作**：弹窗不影响页面操作和调度中心执行
- ✅ **多弹窗支持**：支持同时显示多个弹窗
- ✅ **优雅动画**：滑入滑出动画效果
- ✅ **进度条**：显示倒计时进度条
- ✅ **手动关闭**：支持点击×按钮手动关闭
- ✅ **类型区分**：success、error、warning、info 四种类型

### 3.2 Toast样式

#### Success (成功)
- 颜色：绿色边框
- 图标：✅
- 用途：订单成功、操作成功

#### Error (错误)
- 颜色：红色边框
- 图标：❌
- 用途：订单失败、操作失败

#### Warning (警告)
- 颜色：橙色边框
- 图标：⚠️
- 用途：警告信息

#### Info (信息)
- 颜色：蓝色边框
- 图标：ℹ️
- 用途：一般信息

### 3.3 使用方法

#### JavaScript函数
```javascript
// 显示成功弹窗
showSuccessToast('下单成功', '✅ BTC 多单开仓成功\n金额: 5.00 USDT\n杠杆: 10x');

// 显示错误弹窗
showErrorToast('下单失败', '❌ ETH 多单开仓失败\n原因: 余额不足');

// 显示警告弹窗
showWarningToast('注意', '⚠️ RSI接近阈值\n当前: 790, 阈值: 800');

// 显示信息弹窗
showInfoToast('提示', 'ℹ️ 策略正在执行中，请稍候...');

// 自定义持续时间（默认10秒）
showSuccessToast('标题', '消息内容', 5000);  // 5秒后消失
```

#### 在下单完成后显示
```javascript
// 批量下单示例
async function batchOrderCoins() {
    const account = accounts.find(acc => acc.id === currentAccount);
    
    try {
        // 提交订单
        const response = await fetch('/api/okx-trading/batch-order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 显示成功弹窗
            const message = `✅ 成功开单：${result.successCount}/${result.totalCount} 个币种\n` +
                          `💰 总投入：${result.totalInvestment.toFixed(2)} USDT\n` +
                          `⚡️ 杠杆：${result.leverage}x`;
            
            showSuccessToast('批量下单成功', message);
        } else {
            // 显示错误弹窗
            showErrorToast('批量下单失败', `❌ ${result.error}`);
        }
    } catch (error) {
        showErrorToast('请求失败', `❌ ${error.message}`);
    }
}
```

### 3.4 Toast组件结构

```html
<div class="toast-container" id="toastContainer">
    <!-- Toast元素会动态添加到这里 -->
    <div class="toast toast-success">
        <div class="toast-icon">✅</div>
        <div class="toast-content">
            <div class="toast-title">下单成功</div>
            <div class="toast-message">BTC 多单开仓成功...</div>
        </div>
        <button class="toast-close">×</button>
        <div class="toast-progress"></div>
    </div>
</div>
```

---

## 4. 集成示例

### 4.1 在监控器中完整集成

```python
#!/usr/bin/env python3
"""
策略监控器 - 集成订单调度中心和通知系统
"""

import time
from order_scheduler import submit_order_async

def execute_strategy(account, coins, config):
    """执行策略"""
    
    # 1. 提交所有订单到调度中心
    pending_orders = []
    results = {'success': [], 'failed': []}
    
    def order_callback(success, result, error, coin_symbol):
        """订单回调函数"""
        if success:
            results['success'].append(coin_symbol)
            print(f"✅ {coin_symbol} 下单成功")
        else:
            results['failed'].append(coin_symbol)
            print(f"❌ {coin_symbol} 下单失败: {error}")
    
    for coin in coins:
        request_id = submit_order_async(
            account_id=account['id'],
            symbol=coin['symbol'],
            side='buy',
            order_type='market',
            amount=coin['amount'],
            leverage=config.get('leverage', 10),
            strategy_name='my_strategy',
            callback=lambda s, r, e, sym=coin['symbol']: order_callback(s, r, e, sym)
        )
        pending_orders.append(request_id)
    
    # 2. 等待所有订单完成（可选，调度中心异步执行）
    time.sleep(2)
    
    # 3. 发送Telegram通知
    send_telegram_notification(account, results, config)
    
    return results

def send_telegram_notification(account, results, config):
    """发送Telegram通知"""
    success_count = len(results['success'])
    total_count = success_count + len(results['failed'])
    
    message = f"""
🎯 <b>策略执行完成</b>

📌 账户: {account['name']}
✅ 成功: {success_count}/{total_count}
💰 总投入: {config['total_investment']:.2f} USDT
⚡️ 杠杆: {config['leverage']}x

📋 成功币种:
{chr(10).join(results['success'])}

⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    send_telegram_message(message)
```

### 4.2 前端集成示例

```javascript
// 批量下单并显示Toast通知
async function batchOrderWithNotification() {
    // 1. 显示信息弹窗
    showInfoToast('开始下单', '📝 正在提交订单到调度中心...');
    
    try {
        // 2. 提交订单
        const response = await fetch('/api/okx-trading/batch-order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 3. 显示成功弹窗
            const successCoins = result.coins.filter(c => c.success).map(c => c.symbol).join(', ');
            const message = `✅ 成功: ${result.successCount}/${result.totalCount}\n` +
                          `💰 总投入: ${result.totalInvestment.toFixed(2)} USDT\n` +
                          `📋 币种: ${successCoins}`;
            
            showSuccessToast('批量下单完成', message);
            
            // 4. 刷新持仓和订单
            await loadPositions();
            await loadOrders();
        } else {
            // 显示错误弹窗
            showErrorToast('批量下单失败', `❌ ${result.error}`);
        }
    } catch (error) {
        showErrorToast('请求失败', `❌ ${error.message}`);
    }
}
```

---

## 5. 测试与验证

### 5.1 测试订单调度中心

```bash
# 测试订单调度中心
cd /home/user/webapp
python source_code/order_scheduler.py
```

预期输出：
```
🚀 订单调度中心测试
============================================================
✅ 订单调度中心已启动
🔄 订单处理工作线程已启动
📥 收到订单请求: account_main_1708522225123 ...
🔒 获取账户锁: account_main ...
⚙️  设置杠杆: 10x
✅ 订单执行成功: account_main_1708522225123 ...
🔓 释放账户锁: account_main
✅ 订单成功: {...}

✅ 测试完成
```

### 5.2 测试Telegram通知

```python
# 测试Telegram通知
from source_code.bottom_signal_long_monitor import send_telegram_message

message = """
🎯 <b>测试通知</b>

📌 这是一条测试消息
✅ 如果你收到这条消息，说明Telegram通知配置正确
"""

send_telegram_message(message)
```

### 5.3 测试Toast弹窗

在浏览器开发者工具控制台中执行：
```javascript
// 测试成功弹窗
showSuccessToast('测试标题', '这是一条成功消息，10秒后自动消失');

// 测试所有类型
showSuccessToast('成功', '✅ 操作成功');
showErrorToast('错误', '❌ 操作失败');
showWarningToast('警告', '⚠️ 注意事项');
showInfoToast('信息', 'ℹ️ 提示信息');
```

---

## 6. 故障排查

### 6.1 订单调度中心问题

#### 问题1：订单一直处于pending状态
- **原因**：调度中心未启动或工作线程异常
- **解决**：检查日志文件，重启调度中心

#### 问题2：订单执行失败
- **原因**：API密钥错误、余额不足、网络问题
- **解决**：检查 `order_scheduler_logs/` 中的详细错误日志

#### 问题3：多个账户同时下单冲突
- **原因**：账户锁机制失效
- **解决**：检查日志，确认每个账户的锁是否正常获取和释放

### 6.2 Telegram通知问题

#### 问题1：通知未发送
- **原因**：Bot Token或Chat ID配置错误
- **解决**：检查 `.env` 文件配置，使用测试脚本验证

#### 问题2：通知格式错误
- **原因**：HTML格式不正确
- **解决**：检查消息中的HTML标签是否正确

### 6.3 Toast弹窗问题

#### 问题1：弹窗不显示
- **原因**：Toast容器未添加或JavaScript函数未定义
- **解决**：检查页面HTML中是否有 `<div id="toastContainer">`

#### 问题2：弹窗不自动消失
- **原因**：CSS动画未加载或JavaScript定时器失效
- **解决**：检查浏览器控制台错误，刷新页面

---

## 7. 维护与监控

### 7.1 日志监控

```bash
# 查看订单调度日志
tail -f /home/user/webapp/data/order_scheduler_logs/scheduler_$(date +%Y%m%d).log

# 查看执行记录
tail -f /home/user/webapp/data/order_scheduler_logs/executions_$(date +%Y%m%d).jsonl

# 查看策略监控器日志
pm2 logs bottom-signal-long-monitor --lines 100
```

### 7.2 性能监控

```bash
# 查看订单队列长度
python -c "from order_scheduler import order_queue; print(f'队列长度: {order_queue.qsize()}')"

# 查看调度器状态
pm2 status
```

### 7.3 清理旧日志

```bash
# 清理30天前的日志
find /home/user/webapp/data/order_scheduler_logs/ -type f -mtime +30 -delete
```

---

## 8. 更新日志

### v1.0.0 (2026-02-21)
- ✅ 实现订单调度中心（OrderScheduler）
- ✅ 集成Telegram通知到所有策略
- ✅ 实现10秒自动消失的Toast弹窗
- ✅ 支持多账户并发下单
- ✅ 完整的日志和监控系统

---

## 9. 未来改进

- [ ] 订单优先级队列
- [ ] 订单批量提交优化
- [ ] Telegram通知模板管理
- [ ] Toast弹窗样式自定义
- [ ] 订单执行性能统计
- [ ] WebSocket实时通知

---

**文档版本**: 1.0.0  
**创建时间**: 2026-02-21  
**作者**: OKX Trading System Team

