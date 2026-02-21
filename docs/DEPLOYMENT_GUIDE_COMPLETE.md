# OKX交易系统完整部署文档

**备份时间**: 2026-02-21  
**系统版本**: c23d1a7 (基于 v2.7.0)  
**备份文件**: `/tmp/okx_trading_system_full_backup_20260221.tar.gz`  
**总大小**: ~6.2GB (完整数据，非7天数据)

---

## 📋 目录

1. [系统概述](#系统概述)
2. [备份内容清单](#备份内容清单)
3. [系统依赖](#系统依赖)
4. [完整部署步骤](#完整部署步骤)
5. [配置文件说明](#配置文件说明)
6. [PM2服务配置](#pm2服务配置)
7. [环境变量配置](#环境变量配置)
8. [数据目录结构](#数据目录结构)
9. [Flask路由清单](#flask路由清单)
10. [故障排查](#故障排查)

---

## 系统概述

### 项目结构
```
/home/user/webapp/
├── app.py                          # Flask主应用 (~25000行)
├── requirements.txt                # Python依赖包列表 (235个包)
├── ecosystem.config.js             # PM2服务配置 (27个服务)
├── .env                           # 环境变量配置
├── source_code/                    # Python业务代码
│   ├── *_collector.py             # 数据采集器 (20+个)
│   ├── *_monitor.py               # 监控脚本 (3个)
│   └── utils/                     # 工具函数
├── templates/                      # HTML模板
│   ├── okx_trading.html          # OKX交易页面 (~9000行)
│   ├── coin_change_tracker.html  # 币种追踪页面
│   └── ...                       # 其他页面
├── static/                        # 静态资源
│   ├── css/
│   ├── js/
│   └── images/
├── data/                          # 数据目录 (~800MB - 6GB)
│   ├── okx_auto_strategy/        # 见顶信号策略数据
│   ├── okx_bottom_signal_*/      # 见底信号策略数据
│   ├── market_sentiment/         # 市场情绪数据
│   ├── signals/                  # 信号数据
│   └── [60+个数据子目录]
├── docs/                          # 文档目录 (~15MB)
│   ├── OKX_TRADING_SYSTEM_COMPLETE_DOCUMENTATION.md
│   ├── fix_*.md                  # 修复报告
│   └── ...                       # 其他文档
├── config/                        # 配置文件
├── logs/                          # 日志文件
└── scripts/                       # 工具脚本
```

### 系统统计

| 项目 | 数量 | 大小 | 说明 |
|------|------|------|------|
| **Python文件** | 155 | ~8MB | 主应用、采集器、监控器、工具 |
| **Markdown文档** | 1640 | ~25MB | 系统文档、修复报告、使用指南 |
| **HTML模板** | 10+ | ~3MB | Web界面模板 |
| **配置文件** | 20+ | <1MB | JSON、JS、ENV配置 |
| **数据文件** | 数千 | 6GB+ | JSONL数据文件（完整历史） |
| **依赖包** | 235 | N/A | Python依赖（requirements.txt） |
| **PM2服务** | 27 | N/A | 后台运行服务 |
| **Flask路由** | 200+ | N/A | API端点 |
| **总计** | 2000+ | **6.2GB** | 完整项目备份 |

---

## 备份内容清单

### 核心代码文件
```
✅ app.py                          # Flask主应用
✅ requirements.txt                # Python依赖
✅ ecosystem.config.js             # PM2配置
✅ .env                           # 环境变量
✅ source_code/                    # 业务代码目录
   ├── bottom_signal_long_monitor.py
   ├── okx_tpsl_monitor.py
   ├── rsi_takeprofit_monitor.py
   ├── signal_collector.py
   ├── market_sentiment_collector.py
   ├── price_position_collector.py
   ├── liquidation_1h_collector.py
   ├── sar_slope_collector.py
   ├── new_high_low_collector.py
   ├── price_speed_collector.py
   ├── crypto_index_collector.py
   ├── okx_day_change_collector.py
   ├── panic_wash_collector.py
   ├── sar_bias_stats_collector.py
   ├── price_baseline_collector.py
   ├── price_comparison_collector.py
   ├── financial_indicators_collector.py
   ├── v1v2_collector.py
   ├── coin_change_tracker.py
   ├── okx_trade_history.py
   ├── signal_stats_generator.py
   └── [其他135+个Python文件]
```

### 模板文件
```
✅ templates/
   ├── okx_trading.html           # OKX交易页面 (~9000行)
   ├── coin_change_tracker.html   # 币种追踪页面
   ├── market_sentiment.html      # 市场情绪页面
   ├── signal_stats.html          # 信号统计页面
   ├── liquidation_alert.html     # 清算提醒页面
   ├── panic_wash.html            # 恐慌洗盘页面
   ├── sar_analysis.html          # SAR分析页面
   ├── price_position.html        # 价格位置页面
   ├── crypto_index.html          # 加密指数页面
   └── [其他HTML模板]
```

### 配置文件
```
✅ .env                           # 环境变量（需手动配置API密钥）
✅ ecosystem.config.js             # PM2服务配置
✅ config/
   ├── accounts.json              # 账户配置
   ├── strategies.json            # 策略配置
   └── [其他配置文件]
```

### 数据目录（完整历史数据）
```
✅ data/                          # 6GB+ 完整数据
   ├── okx_auto_strategy/         # 见顶信号策略数据
   ├── okx_bottom_signal_strategies/  # 见底信号配置
   ├── okx_bottom_signal_execution/   # 见底信号执行记录
   ├── okx_tpsl_settings/        # 止盈止损配置
   ├── okx_tpsl_logs/            # 止盈止损日志
   ├── okx_trading_history/      # 交易历史
   ├── market_sentiment/         # 市场情绪数据
   ├── signals/                  # 信号数据
   ├── price_position/           # 价格位置数据
   ├── liquidation_1h/           # 清算数据
   ├── sar_slope/                # SAR斜率数据
   ├── new_high_low/             # 新高新低数据
   ├── price_speed/              # 价格速度数据
   ├── crypto_index_jsonl/       # 加密指数数据
   ├── okx_day_change/           # 日涨跌幅数据
   ├── panic_jsonl/              # 恐慌洗盘数据
   ├── sar_bias_stats/           # SAR偏差统计
   ├── baseline_prices/          # 价格基准数据
   ├── price_comparison/         # 价格对比数据
   ├── financial_indicators/     # 金融指标数据
   ├── v1v2/                     # V1V2数据
   ├── coin_change_tracker/      # 币种变化追踪
   └── [其他40+个数据目录]
```

### 文档目录
```
✅ docs/                          # ~25MB 文档
   ├── OKX_TRADING_SYSTEM_COMPLETE_DOCUMENTATION.md  # 完整技术文档 (58KB)
   ├── rollback_report_6a7bc9c.md                    # 回档报告
   ├── fix_top_signal_switch_persistence.md          # 开关状态修复报告
   ├── fix_summary_top_signal_switch.md              # 修复总结
   ├── fix_top_signal_false_value_loading.md         # false值加载修复
   └── [其他1635+个文档]
```

---

## 系统依赖

### 1. 操作系统依赖 (APT包)

```bash
# 系统基础包
apt-get update
apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    curl \
    wget \
    git \
    vim \
    htop \
    net-tools

# Node.js和npm (用于PM2)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# 其他可能需要的包
apt-get install -y \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev
```

### 2. Python依赖包 (235个)

**核心框架**:
```
Flask==3.1.2                    # Web框架
Flask-Compress==1.23            # HTTP压缩
flask-cors==6.0.2               # CORS支持
Werkzeug==3.1.5                 # WSGI工具库
```

**交易相关**:
```
ccxt==4.5.38                    # 交易所API统一接口
```

**数据处理**:
```
pandas==2.2.3                   # 数据分析
numpy==1.26.4                   # 数值计算
scipy==1.13.1                   # 科学计算
scikit-learn==1.6.1             # 机器学习
```

**定时任务**:
```
APScheduler==3.11.2             # 定时任务调度
schedule==1.2.2                 # 简单定时任务
```

**HTTP请求**:
```
requests==2.32.5                # HTTP请求
aiohttp==3.13.3                 # 异步HTTP
httpx==0.28.1                   # 现代HTTP客户端
```

**数据可视化**:
```
plotly==6.0.1                   # 交互式图表
matplotlib==3.10.3              # 静态图表
seaborn==0.13.2                 # 统计图表
bokeh==3.7.3                    # 交互式可视化
```

**其他工具**:
```
python-dotenv==1.2.1            # 环境变量管理
psutil==7.0.0                   # 系统监控
openpyxl==3.1.5                 # Excel文件处理
beautifulsoup4==4.13.4          # HTML解析
lxml==5.4.0                     # XML解析
```

**完整列表**: 见备份中的 `requirements.txt` (235个包)

### 3. Node.js依赖

```bash
# PM2进程管理器
npm install -g pm2

# PM2日志管理
npm install -g pm2-logrotate
```

### 4. 系统服务依赖

**不需要额外的systemd服务**，所有后台任务由PM2管理。

---

## 完整部署步骤

### 步骤1: 环境准备

```bash
# 1.1 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 1.2 安装系统依赖
sudo apt-get install -y build-essential python3 python3-pip curl git vim

# 1.3 安装Node.js和npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt-get install -y nodejs

# 1.4 安装PM2
sudo npm install -g pm2

# 1.5 验证安装
python3 --version    # 应该 >= 3.10
node --version       # 应该 >= 18.x
npm --version        # 应该 >= 9.x
pm2 --version        # 应该 >= 5.x
```

### 步骤2: 下载并解压备份

```bash
# 2.1 下载备份文件（假设已上传到服务器）
cd /home/user

# 2.2 解压备份
tar -xzf /tmp/okx_trading_system_full_backup_20260221.tar.gz

# 2.3 验证解压
cd webapp
ls -la
# 应该看到：app.py, requirements.txt, ecosystem.config.js, source_code/, data/, 等
```

### 步骤3: 配置环境变量

```bash
# 3.1 复制环境变量模板
cd /home/user/webapp
cp .env.example .env

# 3.2 编辑环境变量（重要！）
vim .env

# 必须配置以下变量：
# OKX_API_KEY_MAIN=your_okx_api_key
# OKX_SECRET_KEY_MAIN=your_okx_secret_key
# OKX_PASSPHRASE_MAIN=your_okx_passphrase
# 
# OKX_API_KEY_FANGFANG12=...
# OKX_SECRET_KEY_FANGFANG12=...
# OKX_PASSPHRASE_FANGFANG12=...
#
# [对其他账户重复以上配置]
#
# TELEGRAM_BOT_TOKEN=your_telegram_bot_token
# TELEGRAM_CHAT_ID=your_telegram_chat_id
```

**⚠️ 重要**: 不要将 `.env` 文件提交到Git仓库！

### 步骤4: 安装Python依赖

```bash
# 4.1 升级pip
cd /home/user/webapp
python3 -m pip install --upgrade pip

# 4.2 安装所有依赖（235个包，需要几分钟）
pip3 install -r requirements.txt

# 4.3 验证关键包
python3 -c "import flask; print('Flask version:', flask.__version__)"
python3 -c "import ccxt; print('CCXT version:', ccxt.__version__)"
python3 -c "import pandas; print('Pandas version:', pandas.__version__)"
```

**可能的问题**:
- 如果某些包安装失败，可能需要安装额外的系统库
- 例如：`sudo apt-get install python3-dev libssl-dev`

### 步骤5: 配置数据目录权限

```bash
# 5.1 确保数据目录存在
cd /home/user/webapp
mkdir -p data logs

# 5.2 设置权限
chmod -R 755 data
chmod -R 755 logs

# 5.3 验证数据目录
ls -la data/
# 应该看到：okx_auto_strategy/, market_sentiment/, signals/, 等
```

### 步骤6: 启动PM2服务

```bash
# 6.1 进入项目目录
cd /home/user/webapp

# 6.2 启动所有服务（27个）
pm2 start ecosystem.config.js

# 6.3 查看服务状态
pm2 list
# 应该看到27个服务都是 'online' 状态

# 6.4 查看Flask应用日志
pm2 logs flask-app --lines 50

# 6.5 保存PM2配置
pm2 save

# 6.6 设置开机自启动
pm2 startup
# 按照输出的命令执行（需要sudo）
```

### 步骤7: 验证系统运行

```bash
# 7.1 检查Flask应用
curl http://localhost:9002/okx-trading
# 应该返回HTML页面

# 7.2 检查API端点
curl http://localhost:9002/api/market-sentiment/latest
# 应该返回JSON数据

# 7.3 检查所有PM2服务
pm2 status
# 确保所有27个服务都是 'online' 状态

# 7.4 查看资源使用
pm2 monit
```

### 步骤8: 配置防火墙（可选）

```bash
# 如果使用ufw
sudo ufw allow 9002/tcp
sudo ufw reload
```

### 步骤9: 设置日志轮转（可选）

```bash
# 安装PM2日志轮转模块
pm2 install pm2-logrotate

# 配置日志轮转
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
```

---

## 配置文件说明

### 1. ecosystem.config.js (PM2配置)

**位置**: `/home/user/webapp/ecosystem.config.js`

**结构**:
```javascript
module.exports = {
  apps: [
    {
      name: "flask-app",
      script: "python3",
      args: "app.py",
      cwd: "/home/user/webapp",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      env: {
        FLASK_APP: "app.py",
        FLASK_ENV: "production",
        PORT: "9002"
      }
    },
    // ... 其他26个服务
  ]
};
```

**27个PM2服务列表**:

| ID | 服务名 | 脚本 | 类型 | 功能 |
|----|--------|------|------|------|
| 1 | signal-collector | signal_collector.py | 采集器 | 市场信号采集 |
| 2 | liquidation-1h-collector | liquidation_1h_collector.py | 采集器 | 清算数据采集 |
| 3 | crypto-index-collector | crypto_index_collector.py | 采集器 | 加密指数采集 |
| 4 | v1v2-collector | v1v2_collector.py | 采集器 | V1V2数据采集 |
| 5 | price-speed-collector | price_speed_collector.py | 采集器 | 价格速度采集 |
| 6 | sar-slope-collector | sar_slope_collector.py | 采集器 | SAR斜率采集 |
| 7 | price-comparison-collector | price_comparison_collector.py | 采集器 | 价格对比采集 |
| 8 | financial-indicators-collector | financial_indicators_collector.py | 采集器 | 金融指标采集 |
| 9 | okx-day-change-collector | okx_day_change_collector.py | 采集器 | 日涨跌幅采集 |
| 10 | price-baseline-collector | price_baseline_collector.py | 采集器 | 价格基准采集 |
| 11 | sar-bias-stats-collector | sar_bias_stats_collector.py | 采集器 | SAR偏差统计 |
| 12 | panic-wash-collector | panic_wash_collector.py | 采集器 | 恐慌洗盘采集 |
| 14 | data-health-monitor | data_health_monitor.py | 监控器 | 数据健康监控 |
| 15 | system-health-monitor | system_health_monitor.py | 监控器 | 系统健康监控 |
| 16 | liquidation-alert-monitor | liquidation_alert_monitor.py | 监控器 | 清算提醒监控 |
| 17 | dashboard-jsonl-manager | dashboard_jsonl_manager.py | 管理器 | 仪表盘数据管理 |
| 18 | gdrive-jsonl-manager | gdrive_jsonl_manager.py | 管理器 | 云盘数据管理 |
| 19 | okx-tpsl-monitor | okx_tpsl_monitor.py | 监控器 | 止盈止损监控 |
| 20 | okx-trade-history | okx_trade_history.py | 采集器 | 交易历史记录 |
| 21 | market-sentiment-collector | market_sentiment_collector.py | 采集器 | 市场情绪采集 |
| 22 | price-position-collector | price_position_collector.py | 采集器 | 价格位置采集 |
| 23 | rsi-takeprofit-monitor | rsi_takeprofit_monitor.py | 监控器 | RSI止盈监控 |
| 24 | new-high-low-collector | new_high_low_collector.py | 采集器 | 新高新低采集 |
| 25 | signal-stats-generator | signal_stats_generator.py | 生成器 | 信号统计生成 |
| 26 | coin-change-tracker | coin_change_tracker.py | 追踪器 | 币种变化追踪 |
| 27 | flask-app | app.py | Web应用 | Flask Web服务器 |
| 28 | bottom-signal-long-monitor | bottom_signal_long_monitor.py | 监控器 | 见底信号做多监控 |

**修改服务配置**:
```bash
# 编辑配置文件
vim ecosystem.config.js

# 重新加载配置
pm2 delete all
pm2 start ecosystem.config.js
pm2 save
```

### 2. .env (环境变量)

**位置**: `/home/user/webapp/.env`

**必需变量**:
```bash
# Flask配置
FLASK_APP=app.py
FLASK_ENV=production
FLASK_PORT=9002
FLASK_HOST=0.0.0.0

# OKX API配置 (主账户)
OKX_API_KEY_MAIN=your_api_key_here
OKX_SECRET_KEY_MAIN=your_secret_key_here
OKX_PASSPHRASE_MAIN=your_passphrase_here

# OKX API配置 (fangfang12账户)
OKX_API_KEY_FANGFANG12=your_api_key_here
OKX_SECRET_KEY_FANGFANG12=your_secret_key_here
OKX_PASSPHRASE_FANGFANG12=your_passphrase_here

# OKX API配置 (anchor账户)
OKX_API_KEY_ANCHOR=your_api_key_here
OKX_SECRET_KEY_ANCHOR=your_secret_key_here
OKX_PASSPHRASE_ANCHOR=your_passphrase_here

# OKX API配置 (poit_main账户)
OKX_API_KEY_POIT_MAIN=your_api_key_here
OKX_SECRET_KEY_POIT_MAIN=your_secret_key_here
OKX_PASSPHRASE_POIT_MAIN=your_passphrase_here

# Binance API配置 (用于价格数据)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# Telegram Bot配置
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 数据目录
DATA_DIR=/home/user/webapp/data
```

**安全提示**:
- ⚠️ 永远不要将 `.env` 文件提交到Git
- ⚠️ 定期更换API密钥
- ⚠️ 使用强密码和2FA保护账户

### 3. requirements.txt (Python依赖)

**位置**: `/home/user/webapp/requirements.txt`

**包含235个包**，主要分类：
- Web框架: Flask, Werkzeug
- 交易接口: ccxt
- 数据处理: pandas, numpy, scipy
- 定时任务: APScheduler, schedule
- HTTP客户端: requests, aiohttp, httpx
- 数据可视化: plotly, matplotlib, seaborn
- 其他工具: 200+ 支持库

**更新依赖**:
```bash
# 更新所有包到最新版本（谨慎操作！）
pip3 install --upgrade -r requirements.txt

# 生成新的requirements.txt
pip3 freeze > requirements_new.txt
```

---

## PM2服务配置

### PM2常用命令

```bash
# 启动服务
pm2 start ecosystem.config.js
pm2 start app.py --name flask-app

# 停止服务
pm2 stop flask-app
pm2 stop all

# 重启服务
pm2 restart flask-app
pm2 restart all

# 删除服务
pm2 delete flask-app
pm2 delete all

# 查看服务列表
pm2 list
pm2 status

# 查看服务详情
pm2 show flask-app
pm2 describe flask-app

# 查看日志
pm2 logs flask-app              # 实时日志
pm2 logs flask-app --lines 100  # 最近100行
pm2 logs flask-app --err        # 只看错误日志

# 监控资源
pm2 monit

# 保存配置
pm2 save

# 开机自启动
pm2 startup
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u user --hp /home/user
pm2 save
```

### PM2服务依赖关系

```
flask-app (核心Web服务)
    ↓ 依赖
├── market-sentiment-collector (市场情绪数据)
├── signal-collector (信号数据)
├── price-position-collector (价格位置数据)
└── coin-change-tracker (币种追踪)

底层采集器（独立运行）:
├── liquidation-1h-collector
├── sar-slope-collector
├── new-high-low-collector
├── price-speed-collector
├── crypto-index-collector
├── okx-day-change-collector
├── panic-wash-collector
├── sar-bias-stats-collector
├── price-baseline-collector
├── price-comparison-collector
├── financial-indicators-collector
└── v1v2-collector

策略监控器（依赖Flask App）:
├── bottom-signal-long-monitor
├── okx-tpsl-monitor
└── rsi-takeprofit-monitor

管理器:
├── dashboard-jsonl-manager
└── gdrive-jsonl-manager

系统监控:
├── data-health-monitor
├── system-health-monitor
└── liquidation-alert-monitor
```

**推荐启动顺序**:
1. 先启动底层采集器（1-2分钟数据准备）
2. 再启动Flask App
3. 最后启动策略监控器

```bash
# 分步启动
pm2 start ecosystem.config.js --only signal-collector,market-sentiment-collector,price-position-collector
sleep 60
pm2 start ecosystem.config.js --only flask-app
sleep 30
pm2 start ecosystem.config.js --only bottom-signal-long-monitor,okx-tpsl-monitor
pm2 start ecosystem.config.js  # 启动剩余所有服务
```

---

## 环境变量配置

### 获取OKX API密钥

1. 登录 https://www.okx.com
2. 进入 **API管理** → **创建API密钥**
3. 设置权限:
   - ✅ 读取权限 (Read)
   - ✅ 交易权限 (Trade)
   - ❌ 提现权限 (Withdraw) - **不要勾选！**
4. 设置IP白名单（可选但推荐）
5. 记录以下信息:
   - API Key
   - Secret Key
   - Passphrase

### 获取Telegram Bot Token

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取Bot Token（格式: `123456:ABCdefGHIjkl...`）

### 获取Telegram Chat ID

```bash
# 方法1: 使用Bot API
# 1. 在Telegram中给你的Bot发送任意消息
# 2. 访问以下URL（替换YOUR_BOT_TOKEN）
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates

# 方法2: 使用Python脚本
python3 << EOF
import requests
BOT_TOKEN = "YOUR_BOT_TOKEN"
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
print(response.json())
EOF
```

在返回的JSON中找到 `"chat":{"id":123456789}` 这就是你的Chat ID。

---

## 数据目录结构

### 数据目录总览
```
data/                           # ~6GB 完整数据
├── okx_auto_strategy/          # 见顶信号策略执行记录
│   ├── account_main_top_signal_top8_short_execution.jsonl
│   ├── account_main_top_signal_bottom8_short_execution.jsonl
│   └── [其他6个账户文件]
│
├── okx_bottom_signal_strategies/  # 见底信号策略配置
│   ├── account_main_bottom_signal_top8_long.jsonl
│   ├── account_main_bottom_signal_bottom8_long.jsonl
│   └── [其他6个配置文件]
│
├── okx_bottom_signal_execution/   # 见底信号执行记录
│   ├── account_main_bottom_signal_top8_long_execution.jsonl
│   ├── account_main_bottom_signal_bottom8_long_execution.jsonl
│   └── [其他6个执行文件]
│
├── okx_tpsl_settings/          # 止盈止损配置
│   ├── account_main_tpsl_settings.json
│   └── [其他3个账户配置]
│
├── okx_tpsl_logs/              # 止盈止损日志
│   └── account_*_tpsl_log_*.jsonl (按日期)
│
├── okx_trading_history/        # 交易历史
│   └── account_*_trades_*.jsonl (按日期)
│
├── market_sentiment/           # 市场情绪数据
│   └── market_sentiment.jsonl (所有历史记录)
│
├── signals/                    # 信号数据
│   └── signals_*.jsonl (按日期)
│
├── price_position/             # 价格位置数据
│   └── price_position.jsonl
│
├── liquidation_1h/             # 清算数据
│   └── liquidation_1h.jsonl
│
├── sar_slope/                  # SAR斜率数据
│   └── sar_slope.jsonl
│
├── new_high_low/               # 新高新低数据
│   ├── coin_highs_lows_state.json
│   └── new_high_low.jsonl
│
├── price_speed/                # 价格速度数据
│   └── price_speed.jsonl
│
├── crypto_index_jsonl/         # 加密指数数据
│   └── crypto_index.jsonl
│
├── okx_day_change/             # 日涨跌幅数据
│   └── okx_day_change.jsonl
│
├── panic_jsonl/                # 恐慌洗盘数据
│   └── panic.jsonl
│
├── sar_bias_stats/             # SAR偏差统计
│   └── sar_bias_stats.jsonl
│
├── baseline_prices/            # 价格基准数据
│   └── baseline_prices.jsonl
│
├── price_comparison/           # 价格对比数据
│   └── price_comparison.jsonl
│
├── financial_indicators/       # 金融指标数据
│   └── financial_indicators.jsonl
│
├── v1v2/                       # V1V2数据
│   └── v1v2.jsonl
│
├── coin_change_tracker/        # 币种变化追踪
│   └── coin_change_tracker.jsonl
│
└── [其他40+个数据目录]
```

### JSONL文件格式

**市场情绪数据示例** (`market_sentiment/market_sentiment.jsonl`):
```json
{
  "timestamp": "2026-02-21T14:00:00.123456",
  "market_metrics": {
    "up_ratio": 45.5,
    "down_ratio": 54.5,
    "total_coins": 15
  },
  "rsi_analysis": {
    "rsi_sum": 1850.5,
    "rsi_avg": 123.37
  },
  "signals": {
    "has_top_signal": true,
    "has_bottom_signal": false
  }
}
```

**交易历史示例** (`okx_trading_history/account_main_trades_2026-02-21.jsonl`):
```json
{
  "timestamp": "2026-02-21T13:30:15.123456",
  "account_id": "account_main",
  "coin": "BTC",
  "side": "sell",
  "amount_usd": 5.0,
  "price": 41666.67,
  "leverage": 10,
  "status": "filled"
}
```

---

## Flask路由清单

### 主要路由分类

**1. 页面路由** (HTML模板):
```python
@app.route('/')                           # 首页
@app.route('/okx-trading')                # OKX交易页面
@app.route('/coin-change-tracker')        # 币种追踪页面
@app.route('/market-sentiment')           # 市场情绪页面
@app.route('/signal-stats')               # 信号统计页面
# ... 其他10+个页面路由
```

**2. OKX交易API** (50+ routes):
```python
# 账户管理
@app.route('/api/okx-trading/accounts', methods=['GET', 'POST'])
@app.route('/api/okx-trading/account/<account_id>', methods=['GET', 'PUT', 'DELETE'])

# 见顶信号策略
@app.route('/api/okx-trading/set-allowed-top-signal/<account_id>/<strategy_type>', methods=['POST'])
@app.route('/api/okx-trading/check-top-signal-status/<account_id>/<strategy_type>', methods=['GET'])

# 见底信号策略
@app.route('/api/okx-trading/save-bottom-signal-config/<account_id>/<strategy_type>', methods=['POST'])
@app.route('/api/okx-trading/get-bottom-signal-config/<account_id>/<strategy_type>', methods=['GET'])
@app.route('/api/okx-trading/set-allowed-bottom-signal/<account_id>/<strategy_type>', methods=['POST'])
@app.route('/api/okx-trading/check-bottom-signal-status/<account_id>/<strategy_type>', methods=['GET'])

# 止盈止损
@app.route('/api/okx-trading/tpsl-settings/<account_id>', methods=['GET', 'POST'])
@app.route('/api/okx-trading/positions/<account_id>', methods=['GET'])

# 交易历史
@app.route('/api/okx-trading/trade-history/<account_id>', methods=['GET'])
@app.route('/api/okx-trading/account-info/<account_id>', methods=['GET'])
```

**3. 市场数据API** (30+ routes):
```python
@app.route('/api/market-sentiment/latest', methods=['GET'])
@app.route('/api/market-sentiment/history', methods=['GET'])
@app.route('/api/signals/latest', methods=['GET'])
@app.route('/api/price-position/latest', methods=['GET'])
@app.route('/api/liquidation/latest', methods=['GET'])
# ... 其他25+个市场数据路由
```

**4. 数据查询API** (40+ routes):
```python
@app.route('/api/coin-change/latest', methods=['GET'])
@app.route('/api/sar-slope/latest', methods=['GET'])
@app.route('/api/new-high-low/latest', methods=['GET'])
@app.route('/api/price-speed/latest', methods=['GET'])
# ... 其他36+个数据查询路由
```

**5. 系统管理API** (20+ routes):
```python
@app.route('/api/health', methods=['GET'])
@app.route('/api/system-info', methods=['GET'])
@app.route('/api/logs/<service_name>', methods=['GET'])
@app.route('/api/restart-service/<service_name>', methods=['POST'])
# ... 其他16+个系统管理路由
```

**完整路由清单**: 200+ 路由，详见 `app.py`

### 测试路由

```bash
# 测试首页
curl http://localhost:9002/

# 测试OKX交易页面
curl http://localhost:9002/okx-trading

# 测试API端点
curl http://localhost:9002/api/market-sentiment/latest
curl http://localhost:9002/api/okx-trading/accounts
curl http://localhost:9002/api/health
```

---

## 故障排查

### 常见问题1: Flask应用无法启动

**症状**: `pm2 list` 显示 flask-app 状态为 `errored`

**排查步骤**:
```bash
# 1. 查看详细日志
pm2 logs flask-app --lines 200

# 2. 手动启动测试
cd /home/user/webapp
python3 app.py
# 查看错误信息

# 3. 检查端口占用
lsof -i :9002
# 如果被占用，杀掉进程或更改端口

# 4. 检查Python版本
python3 --version
# 确保 >= 3.10

# 5. 检查依赖包
pip3 list | grep -E "Flask|ccxt|pandas"
```

**常见原因**:
- ❌ 缺少依赖包 → 运行 `pip3 install -r requirements.txt`
- ❌ 端口被占用 → 更改 `.env` 中的 `FLASK_PORT`
- ❌ 环境变量未配置 → 检查 `.env` 文件
- ❌ Python版本太低 → 升级到 Python 3.10+

### 常见问题2: 采集器无法启动

**症状**: 某个采集器服务一直重启或报错

**排查步骤**:
```bash
# 1. 查看特定服务日志
pm2 logs market-sentiment-collector --lines 100

# 2. 检查API密钥
# 编辑 .env 文件，确保密钥正确

# 3. 测试API连接
python3 << EOF
import ccxt
okx = ccxt.okx({
    'apiKey': 'YOUR_KEY',
    'secret': 'YOUR_SECRET',
    'password': 'YOUR_PASSPHRASE'
})
print(okx.fetch_balance())
EOF

# 4. 检查数据目录权限
ls -la data/market_sentiment/
chmod -R 755 data/
```

### 常见问题3: PM2服务无法保存

**症状**: 重启服务器后PM2服务全部丢失

**解决方案**:
```bash
# 1. 保存PM2配置
pm2 save

# 2. 设置开机自启动
pm2 startup
# 复制输出的命令并执行（需要sudo）

# 3. 验证
pm2 list
sudo reboot
# 重启后再次检查
pm2 list
```

### 常见问题4: 数据目录权限问题

**症状**: 日志显示 "Permission denied" 错误

**解决方案**:
```bash
cd /home/user/webapp
sudo chown -R $USER:$USER data/
chmod -R 755 data/
chmod -R 755 logs/
```

### 常见问题5: 内存不足

**症状**: 服务频繁重启，系统响应缓慢

**排查步骤**:
```bash
# 1. 检查内存使用
free -h
pm2 monit

# 2. 设置内存限制
# 编辑 ecosystem.config.js
# max_memory_restart: "300M"  # 根据服务调整

# 3. 减少不必要的服务
pm2 stop [不需要的服务名]
pm2 delete [不需要的服务名]
pm2 save
```

### 常见问题6: Git推送失败

**症状**: `git push` 被拒绝

**解决方案**:
```bash
# 1. 如果在detached HEAD状态
git checkout -b fix-branch
git push origin fix-branch

# 2. 或者强制推送（谨慎！）
git push -f origin master

# 3. 或者先pull再push
git pull --rebase origin master
git push origin master
```

---

## 性能优化建议

### 1. 数据库索引（如果使用）
```sql
-- 为常用查询字段创建索引
CREATE INDEX idx_timestamp ON trades(timestamp);
CREATE INDEX idx_account_id ON trades(account_id);
```

### 2. JSONL文件优化
```bash
# 定期归档旧数据
cd /home/user/webapp/data
mkdir -p archive/2026-02

# 移动30天前的数据
find okx_trading_history/ -name "*.jsonl" -mtime +30 -exec mv {} archive/2026-02/ \;

# 压缩归档
tar -czf archive_2026-02.tar.gz archive/2026-02/
rm -rf archive/2026-02/
```

### 3. PM2集群模式（Flask App）
```javascript
// ecosystem.config.js
{
  name: "flask-app",
  script: "gunicorn",
  args: "-w 4 -b 0.0.0.0:9002 app:app",
  instances: 1,
  exec_mode: "fork"
}
```

### 4. Nginx反向代理（推荐）
```nginx
# /etc/nginx/sites-available/okx-trading
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:9002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 备份与恢复

### 创建备份
```bash
# 完整备份（包含所有数据）
cd /home/user
tar -czf okx_trading_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    webapp/app.py \
    webapp/requirements.txt \
    webapp/ecosystem.config.js \
    webapp/.env \
    webapp/source_code/ \
    webapp/templates/ \
    webapp/static/ \
    webapp/data/ \
    webapp/docs/

# 代码备份（不含数据，快速）
tar -czf okx_trading_code_$(date +%Y%m%d_%H%M%S).tar.gz \
    webapp/app.py \
    webapp/requirements.txt \
    webapp/ecosystem.config.js \
    webapp/source_code/ \
    webapp/templates/ \
    webapp/docs/
```

### 恢复备份
```bash
# 停止所有服务
pm2 stop all

# 恢复备份
cd /home/user
tar -xzf okx_trading_backup_YYYYMMDD_HHMMSS.tar.gz

# 重启服务
cd webapp
pm2 restart all
```

### 自动备份脚本
```bash
# /home/user/backup_okx_trading.sh
#!/bin/bash
BACKUP_DIR="/home/user/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cd /home/user

# 备份代码和配置
tar -czf $BACKUP_DIR/okx_trading_code_$DATE.tar.gz \
    webapp/app.py \
    webapp/requirements.txt \
    webapp/ecosystem.config.js \
    webapp/source_code/ \
    webapp/templates/

# 备份数据（7天内）
find webapp/data/ -type f -mtime -7 | tar -czf $BACKUP_DIR/okx_trading_data_7d_$DATE.tar.gz -T -

# 删除30天前的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

设置自动备份:
```bash
chmod +x /home/user/backup_okx_trading.sh
crontab -e
# 添加: 0 2 * * * /home/user/backup_okx_trading.sh
```

---

## 附录

### A. 端口清单
- **9002**: Flask Web应用（OKX交易页面）
- **其他**: 所有PM2服务不占用端口，只有Flask监听9002

### B. 重要文件路径
```
/home/user/webapp/app.py                   # Flask主应用
/home/user/webapp/.env                    # 环境变量（需配置）
/home/user/webapp/ecosystem.config.js     # PM2配置
/home/user/webapp/requirements.txt        # Python依赖
/home/user/webapp/data/                   # 数据目录
/home/user/webapp/logs/                   # 日志目录
/home/user/webapp/docs/                   # 文档目录
```

### C. 联系方式
- GitHub: https://github.com/jamesyidc/25669889956
- Issues: https://github.com/jamesyidc/25669889956/issues

---

**文档版本**: 1.0  
**最后更新**: 2026-02-21  
**文档作者**: GenSpark AI  
**系统版本**: c23d1a7

---

## 快速参考卡片

```
┌──────────────────────────────────────────────────────────────┐
│ OKX交易系统快速参考                                           │
├──────────────────────────────────────────────────────────────┤
│ 启动系统: pm2 start ecosystem.config.js                      │
│ 停止系统: pm2 stop all                                       │
│ 重启系统: pm2 restart all                                    │
│ 查看日志: pm2 logs flask-app                                 │
│ 查看状态: pm2 list                                           │
│ 监控资源: pm2 monit                                          │
│                                                              │
│ 访问页面: http://localhost:9002/okx-trading                 │
│ 测试API:  curl http://localhost:9002/api/health             │
│                                                              │
│ 配置文件: /home/user/webapp/.env                            │
│ 数据目录: /home/user/webapp/data/                           │
│ 日志目录: /home/user/webapp/logs/                           │
│                                                              │
│ Python版本: >= 3.10                                         │
│ Node版本:   >= 18.x                                         │
│ PM2服务数:  27个                                            │
│ Flask路由:  200+个                                          │
└──────────────────────────────────────────────────────────────┘
```
