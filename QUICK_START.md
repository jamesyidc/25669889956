# OKX交易系统 - 快速启动指南

## 🚀 一键启动命令

### 启动所有服务
```bash
cd /home/user/webapp
pm2 start ecosystem.config.js
pm2 save
```

### 查看服务状态
```bash
pm2 list
pm2 status
```

### 运行健康检查
```bash
cd /home/user/webapp
./test_system_health.sh
```

## 🌐 访问系统

**公网URL**: https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai

### 主要页面
- 主页: `/`
- OKX交易标记 V3: `/okx-trading-marks-v3`
- 恐慌指标 V3: `/panic-v3`
- 价格位置 V2: `/price-position-v2`

## 📊 核心API端点

### 币种追踪
```bash
curl http://localhost:9002/api/coin-change-tracker/latest
```

### 市场情绪
```bash
curl http://localhost:9002/api/market-sentiment/latest
```

### OKX TPSL设置
```bash
curl http://localhost:9002/api/okx-trading/tpsl-settings/account_main
```

## 🔧 常用管理命令

### PM2进程管理
```bash
pm2 list                    # 查看所有进程
pm2 logs [name]            # 查看日志
pm2 restart [name]         # 重启进程
pm2 restart all            # 重启所有进程
pm2 stop all               # 停止所有进程
pm2 reload ecosystem.config.js  # 重载配置
```

### 查看实时日志
```bash
pm2 logs flask-app         # Flask应用日志
pm2 logs okx-tpsl-monitor  # OKX监控日志
pm2 logs --lines 50        # 查看所有日志(最近50行)
```

## 📁 重要文件位置

### 配置文件
- `.env` - 环境变量(Telegram配置)
- `okx_accounts.json` - OKX账户凭证
- `okx_account_limits.json` - 账户限制
- `ecosystem.config.js` - PM2配置

### 数据目录
- `data/` - JSONL数据文件
- `logs/` - PM2日志文件
- `source_code/` - 采集器源代码

## 🔍 故障排除

### 检查进程状态
```bash
pm2 list
pm2 status
```

### 查看错误日志
```bash
pm2 logs flask-app --err --lines 50
pm2 logs okx-tpsl-monitor --err --lines 50
```

### 重启单个服务
```bash
pm2 restart flask-app
pm2 restart okx-tpsl-monitor
```

### 重启所有服务
```bash
pm2 restart all
```

### 清理并重启
```bash
pm2 delete all
pm2 start ecosystem.config.js
pm2 save
```

## ✅ 系统验证

运行健康检查脚本验证所有功能：
```bash
./test_system_health.sh
```

应该看到所有检查都通过 ✅

## 📦 系统组件

### 24个运行的服务

#### Web应用 (1)
- flask-app

#### 数据采集器 (13)
- signal-collector
- liquidation-1h-collector
- crypto-index-collector
- v1v2-collector
- price-speed-collector
- sar-slope-collector
- price-comparison-collector
- financial-indicators-collector
- okx-day-change-collector
- price-baseline-collector
- sar-bias-stats-collector
- panic-wash-collector
- coin-change-tracker

#### 监控服务 (4)
- data-health-monitor
- system-health-monitor
- liquidation-alert-monitor
- rsi-takeprofit-monitor

#### JSONL管理器 (2)
- dashboard-jsonl-manager
- gdrive-jsonl-manager

#### OKX交易系统 (2)
- okx-tpsl-monitor
- okx-trade-history

#### 市场分析 (2)
- market-sentiment-collector
- price-position-collector

## 🎯 功能特性

### ✅ 已实现
- [x] 自动数据采集
- [x] 实时市场监控
- [x] OKX交易管理
- [x] 止盈止损自动监控
- [x] JSONL数据管理
- [x] Telegram通知
- [x] 健康检查系统

### 📈 数据收集
- 实时价格数据
- 技术指标(RSI, SAR等)
- 爆仓数据
- 市场情绪分析

### 🤖 自动化功能
- 自动策略执行
- 批量订单处理
- 风险监控
- 数据备份

## 📞 支持

如有问题，请查看：
1. PM2日志: `pm2 logs`
2. 系统日志: `logs/` 目录
3. 健康检查: `./test_system_health.sh`

---

**部署版本**: v3.0  
**最后更新**: 2026-02-21  
**状态**: ✅ 生产就绪
