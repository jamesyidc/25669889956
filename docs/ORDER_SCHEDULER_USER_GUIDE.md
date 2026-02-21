# 订单调度中心使用指南

## 快速开始

### 访问地址
🌐 **订单调度中心**: https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/order-scheduler

---

## 界面说明

### 1. 状态卡片
显示调度中心的实时运行状态：
- **运行状态**: 绿色✅表示正常运行
- **队列大小**: 当前等待处理的订单数量
- **锁定账户**: 正在执行订单的账户列表
- **总账户数**: 系统配置的账户总数

### 2. 今日统计
显示今天的订单执行情况：
- **总订单数**: 今天提交的订单总数
- **成功订单**: 成功执行的订单数
- **失败订单**: 执行失败的订单数
- **成功率**: 成功订单占比

### 3. 订单历史
显示最近的订单执行记录：
- 默认显示最近100条
- 可通过下拉菜单按账户筛选
- 颜色标识：
  - 🟢 绿色 = 成功
  - 🔴 红色 = 失败
  - 🟡 黄色 = 处理中

### 4. 详细统计
三个统计面板：
- **今日 vs 昨日**: 对比数据
- **按账户统计**: 各账户的订单分布
- **按策略统计**: 各策略的执行情况

---

## 主要功能

### 自动刷新
- 界面每5秒自动刷新一次
- 无需手动刷新页面
- 实时显示最新数据

### 订单过滤
1. 点击"订单历史"卡片中的下拉菜单
2. 选择要查看的账户
3. 选择"所有账户"可查看全部订单

### 查看详情
每条订单记录包含：
- 🕐 **执行时间**: 订单执行的时间戳
- 👤 **账户**: 执行订单的账户ID
- 💱 **交易对**: 交易的币对（如BTC/USDT:USDT）
- ↕️ **方向**: buy（买入）或sell（卖出）
- 📊 **数量**: 交易数量
- 🎯 **策略**: 触发订单的策略名称
- ✅/❌ **状态**: 订单执行结果

---

## API使用

### 1. 获取状态
```bash
curl https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/api/order-scheduler/status
```

### 2. 查询订单历史
```bash
# 查询所有订单
curl https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/api/order-scheduler/orders

# 查询特定账户
curl "https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/api/order-scheduler/orders?account=account_main"
```

### 3. 获取统计信息
```bash
curl https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/api/order-scheduler/stats
```

### 4. 提交订单
```bash
curl -X POST https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/api/order-scheduler/submit \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "account_main",
    "symbol": "BTC/USDT:USDT",
    "side": "buy",
    "order_type": "market",
    "amount": 0.001,
    "leverage": 10,
    "strategy_name": "manual"
  }'
```

---

## 常见问题

### Q1: 为什么看不到订单历史？
**A**: 可能原因：
- 今天还没有执行过任何订单
- 日志文件不存在
- 所有订单都是昨天之前的

### Q2: 如何知道订单是否执行成功？
**A**: 查看方式：
- 订单历史列表中的状态颜色
- 今日统计卡片中的成功/失败数量
- 详细统计面板中的成功率

### Q3: 多账户同时下单会冲突吗？
**A**: 不会！调度中心的特点：
- 每个账户有独立的锁
- 同一账户的订单串行执行
- 不同账户的订单并行处理
- 队列机制确保所有订单都能执行

### Q4: 界面不刷新怎么办？
**A**: 解决方法：
1. 检查浏览器控制台是否有错误
2. 手动刷新浏览器页面（F5）
3. 检查网络连接是否正常

---

## 监控建议

### 日常检查
1. **每天查看今日统计**
   - 确认成功率是否正常（应>95%）
   - 检查失败订单的原因

2. **定期查看订单历史**
   - 确认重要订单已执行
   - 检查订单执行时间是否合理

3. **关注队列大小**
   - 正常情况应该是0或很小的数字
   - 如果持续很大，说明可能有问题

### 异常警报
如果发现以下情况，需要立即处理：
- ⚠️ 运行状态显示红色
- ⚠️ 成功率低于80%
- ⚠️ 队列大小持续增长
- ⚠️ 同一账户长时间被锁定

---

## 数据保留策略

### 日志文件
- 位置: `data/order_scheduler_logs/`
- 格式: `executions_YYYYMMDD.jsonl`
- 保留: 建议保留30天

### 查询范围
- 订单历史: 显示最近2天的数据
- 详细统计: 今日和昨日对比
- API查询: 可自定义limit参数

---

## 性能参考

### 响应时间
- 状态查询: <50ms
- 订单历史: <100ms
- 统计信息: <150ms
- 提交订单: <100ms

### 资源占用
- 内存: ~10MB
- CPU: <1%（空闲时）
- 磁盘: ~1MB/天（日志）

---

## 相关链接

- **主交易系统**: https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/okx-trading
- **GitHub仓库**: https://github.com/jamesyidc/25669889956
- **最新PR**: https://github.com/jamesyidc/25669889956/pull/2
- **完整文档**: `/home/user/webapp/docs/ORDER_SCHEDULER_VISUALIZATION_COMPLETE.md`

---

## 技术支持

遇到问题？
1. 查看完整文档
2. 检查Flask应用日志：`pm2 logs flask-app`
3. 查看调度中心日志：`cat data/order_scheduler_logs/executions_*.jsonl`
4. 在GitHub提交Issue

---

**最后更新**: 2026-02-21  
**版本**: v1.0  
**状态**: ✅ 可用
