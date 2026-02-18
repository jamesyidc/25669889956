# OKX 交易系统 - 完整部署指南

## 📦 备份内容清单

### 1. 核心代码（~5MB）
```
/home/user/webapp/
├── app.py                    # Flask主应用（18000+行）
├── source_code/             # Python采集器与工具
│   ├── *_collector.py       # 数据采集器（88个Python文件）
│   ├── *_manager.py         # 管理器脚本
│   └── okx_tpsl_monitor.py  # 止盈止损监控
└── config/                   # 配置文件
    └── telegram_config.py    # Telegram配置
```

### 2. Web界面（~2MB）
```
templates/                    # HTML模板（88个文件）
├── okx_trading.html         # OKX交易主页面
├── price_position_unified.html
├── panic_new.html
└── ...

static/                       # 静态资源
├── css/
├── js/
└── images/
```

### 3. 数据文件（~800MB）
```
data/                         # JSONL数据文件（数千个文件）
├── okx_auto_strategy/       # 策略配置与执行记录
├── okx_tpsl_settings/       # 止盈止损配置
├── signal_stats/            # 信号统计数据
├── price_position_*/        # 价格与持仓数据
├── panic_wash_*/            # 恐慌洗盘数据
└── ...（~50个子目录）
```

### 4. 文档（~15MB）
```
*.md                          # Markdown文档（440个文件）
├── README.md
├── DEPLOYMENT_GUIDE.md      # 本文档
├── TPSL_MONITORING_SETUP_GUIDE.md
├── ORDER_SIZE_LIMIT_EXPLANATION.md
└── ...（各种修复报告、使用指南）
```

### 5. 依赖环境
```
requirements.txt              # Python依赖包列表
package.json                  # Node.js依赖包列表
ecosystem.config.js          # PM2进程配置
```

---

## 🔧 系统依赖关系

### Python 环境
```bash
Python 3.11+
pip 包管理器

主要依赖包：
- Flask==3.0.0              # Web框架
- requests==2.31.0          # HTTP客户端
- APScheduler==3.10.4       # 定时任务
- pandas==2.1.3             # 数据处理
- numpy==1.26.2             # 数值计算
```

### Node.js 环境
```bash
Node.js 18+
npm 包管理器
PM2 进程管理器

全局包：
- pm2@latest                # 进程管理器
```

### 系统包（APT）
```bash
apt install -y \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    curl \
    jq \
    htop
```

---

## 📂 完整备份文件

### 备份文件信息
```
文件名：webapp_full_backup_20260217_145900.tar.gz
位置：/tmp/webapp_full_backup_20260217_145900.tar.gz
大小：~2GB（压缩后约500-800MB）
包含：所有代码、配置、数据、文档
```

### 备份包含的内容
1. ✅ **完整代码**：所有Python、HTML、JavaScript文件
2. ✅ **所有数据**：全部JSONL数据文件（不是7天，是全部）
3. ✅ **配置文件**：Flask配置、PM2配置、Telegram配置
4. ✅ **文档**：所有Markdown文档、使用指南
5. ✅ **依赖清单**：requirements.txt、package.json
6. ✅ **PM2配置**：ecosystem.config.js（32个服务配置）
7. ❌ **不包含**：node_modules/（太大，需重新安装）
8. ❌ **不包含**：Python虚拟环境venv/（需重新创建）

---

## 🚀 重新部署步骤（从零开始）

### 第1步：系统准备（10分钟）

#### 1.1 安装系统依赖
```bash
# 更新包列表
sudo apt update

# 安装必需的系统包
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    curl \
    jq \
    htop \
    tmux

# 验证安装
python3 --version  # 应该 >= 3.11
node --version     # 应该 >= 18
npm --version
```

#### 1.2 安装PM2
```bash
# 全局安装PM2
sudo npm install -g pm2

# 验证安装
pm2 --version

# 设置PM2开机启动（可选）
pm2 startup
# 按照提示执行命令
```

---

### 第2步：恢复备份（5分钟）

#### 2.1 解压备份文件
```bash
# 创建目标目录
mkdir -p /home/user/webapp

# 解压备份文件
cd /home/user
tar -xzf /tmp/webapp_full_backup_20260217_145900.tar.gz

# 验证解压
ls -lh /home/user/webapp
```

#### 2.2 设置权限
```bash
# 设置目录权限
chmod -R 755 /home/user/webapp

# 设置Python脚本执行权限
chmod +x /home/user/webapp/source_code/*.py
```

---

### 第3步：安装Python依赖（5-10分钟）

#### 3.1 创建虚拟环境（推荐）
```bash
cd /home/user/webapp

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

#### 3.2 安装依赖包
```bash
# 安装所有Python依赖
pip install -r requirements.txt

# 验证安装
pip list | grep -E "Flask|requests|pandas|APScheduler"
```

**关键依赖包**：
- Flask（Web框架）
- requests（HTTP客户端）
- pandas（数据处理）
- APScheduler（定时任务）
- hmac, hashlib, base64（加密）

---

### 第4步：配置环境（5分钟）

#### 4.1 配置Telegram（可选）
```bash
# 编辑Telegram配置
nano /home/user/webapp/config/telegram_config.py

# 填入您的Bot Token和Chat ID
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'
```

#### 4.2 检查数据目录
```bash
# 验证数据目录存在
ls -lh /home/user/webapp/data/

# 应该看到：
# okx_auto_strategy/
# okx_tpsl_settings/
# signal_stats/
# price_position_*/
# 等50+个子目录
```

---

### 第5步：启动服务（10分钟）

#### 5.1 启动Flask Web应用
```bash
cd /home/user/webapp

# 使用PM2启动Flask
pm2 start ecosystem.config.js --only flask-app

# 查看日志
pm2 logs flask-app --lines 20
```

**预期输出**：
```
flask-app  |  * Running on http://127.0.0.1:9002
flask-app  |  * Running on http://169.254.0.21:9002
```

#### 5.2 启动所有采集器
```bash
# 启动全部32个服务
pm2 start ecosystem.config.js

# 查看状态
pm2 list

# 预期看到32个服务（31个online，1个stopped）
```

**32个服务列表**：
1. flask-app
2. signal-collector
3. liquidation-1h-collector
4. crypto-index-collector
5. v1v2-collector
6. price-speed-collector
7. sar-slope-collector
8. price-comparison-collector
9. financial-indicators-collector
10. okx-day-change-collector
11. price-baseline-collector
12. sar-bias-stats-collector
13. panic-wash-collector
14. liquidation-alert-monitor
15. dashboard-jsonl-manager
16. gdrive-jsonl-manager
17. okx-trade-history-collector
18. okx-trading-marks-collector
19. coin-change-tracker
20. system-health-monitor-v2
21. price-position-collector
22. new-high-low-collector
23. okx-tpsl-monitor
24. signal-stats-generator-v2

#### 5.3 验证服务运行
```bash
# 检查Flask是否正常
curl http://localhost:9002/

# 检查API端点
curl http://localhost:9002/api/okx-trading/default-account

# 查看所有服务状态
pm2 status

# 查看特定服务日志
pm2 logs flask-app --nostream --lines 50
```

---

### 第6步：访问Web界面（1分钟）

#### 6.1 获取访问地址
```bash
# 如果在本地
http://localhost:9002

# 如果在远程服务器（使用SSH端口转发）
ssh -L 9002:localhost:9002 user@your-server-ip
# 然后访问 http://localhost:9002
```

#### 6.2 主要页面
```
主页：http://localhost:9002/
OKX交易：http://localhost:9002/okx-trading
价格持仓：http://localhost:9002/price-position
恐慌监控：http://localhost:9002/panic
数据管理：http://localhost:9002/data-management
```

---

## 🔄 PM2服务配置详解

### ecosystem.config.js 结构
```javascript
module.exports = {
  apps: [
    // 1. Flask Web应用（端口9002）
    {
      name: 'flask-app',
      script: 'venv/bin/python3',
      args: 'app.py',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        FLASK_APP: 'app.py',
        FLASK_ENV: 'production'
      }
    },
    
    // 2. 数据采集器（定时执行）
    {
      name: 'signal-collector',
      script: 'venv/bin/python3',
      args: 'source_code/signal_collector.py',
      cwd: '/home/user/webapp',
      cron_restart: '*/5 * * * *',  // 每5分钟
      autorestart: false,
      watch: false
    },
    
    // 3. 止盈止损监控（每60秒）
    {
      name: 'okx-tpsl-monitor',
      script: 'venv/bin/python3',
      args: 'source_code/okx_tpsl_monitor.py',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false
    },
    
    // ... 其他29个服务
  ]
};
```

### 服务类型与频率
| 服务类型 | 数量 | 执行频率 | 说明 |
|---------|------|---------|------|
| Web应用 | 1 | 持续运行 | Flask (端口9002) |
| 实时监控 | 3 | 持续运行 | 止盈止损、恐慌洗盘 |
| 高频采集 | 8 | 每5分钟 | 价格、信号、清算 |
| 中频采集 | 12 | 每15-30分钟 | 交易记录、指标 |
| 低频采集 | 6 | 每1-4小时 | 统计、分析 |
| 管理器 | 2 | 按需触发 | 数据管理 |

---

## 🗂️ 数据文件对应关系

### 数据目录结构
```
/home/user/webapp/data/
├── okx_auto_strategy/                 # OKX自动策略
│   ├── account_main.json             # 账户配置+API凭证
│   ├── account_main_upratio0_top8_execution.jsonl
│   └── ...
│
├── okx_tpsl_settings/                # 止盈止损配置
│   ├── account_main_tpsl.jsonl      # 止盈止损阈值
│   ├── account_main_tpsl_execution.jsonl  # 执行记录
│   └── account_main_history.jsonl   # 修改历史
│
├── signal_stats/                     # 信号统计数据
│   ├── signal_stats_buy_YYYYMMDD.jsonl
│   └── signal_stats_sell_YYYYMMDD.jsonl
│
├── price_position_YYYYMMDD.jsonl    # 价格持仓数据（每日）
├── panic_wash_YYYYMMDD.jsonl        # 恐慌洗盘数据
├── okx_day_change_YYYYMMDD.jsonl    # OKX日涨跌幅
└── ... （50+个数据文件类型）
```

### 数据文件大小分布
```
price_position_*.jsonl    : ~50MB/天  × 30天  = 1.5GB
panic_wash_*.jsonl        : ~20MB/天  × 30天  = 600MB
okx_day_change_*.jsonl    : ~5MB/天   × 30天  = 150MB
signal_stats/             : ~10MB/天  × 30天  = 300MB
其他数据文件              :                     ~450MB
─────────────────────────────────────────────
总计                      :                    ~3GB
```

**备份包含全部历史数据，不是只有7天！**

---

## 🔐 API凭证配置

### OKX API凭证存储
```
文件位置：/home/user/webapp/data/okx_auto_strategy/account_*.json

示例内容：
{
  "enabled": true,
  "triggerPrice": 66000,
  "strategyType": "bottom_performers",
  "apiKey": "YOUR_API_KEY",
  "apiSecret": "YOUR_API_SECRET",
  "passphrase": "YOUR_PASSPHRASE",
  "max_order_size": 5,
  "lastUpdated": "2026-02-17 14:48:00"
}
```

**配置方法**：
1. 在OKX交易页面点击"保存设置"按钮
2. 系统自动保存API凭证到服务器
3. 止盈止损监控服务读取此文件

---

## 📊 路由配置清单

### Flask路由（80+个API端点）

#### 主要页面路由
```python
@app.route('/')                              # 主页
@app.route('/okx-trading')                   # OKX交易页面
@app.route('/price-position')                # 价格持仓页面
@app.route('/panic')                         # 恐慌监控页面
@app.route('/data-management')               # 数据管理页面
```

#### OKX交易API
```python
@app.route('/api/okx-trading/default-account')              # 默认账户
@app.route('/api/okx-trading/account-balance')              # 账户余额
@app.route('/api/okx-trading/positions')                    # 持仓信息
@app.route('/api/okx-trading/pending-orders')               # 委托订单
@app.route('/api/okx-trading/place-order', methods=['POST']) # 下单
@app.route('/api/okx-trading/cancel-order', methods=['POST'])# 撤单
@app.route('/api/okx-trading/tpsl-settings/<account_id>')   # 止盈止损配置
@app.route('/api/okx-trading/save-account-credentials/<account_id>', methods=['POST']) # 保存API凭证
```

#### 数据API
```python
@app.route('/api/price-position/data')                      # 价格持仓数据
@app.route('/api/panic/data')                               # 恐慌洗盘数据
@app.route('/api/signal-stats/data')                        # 信号统计数据
@app.route('/api/coin-change-tracker/history')              # 币种变化历史
```

#### 管理API
```python
@app.route('/api/server-date')                              # 服务器日期
@app.route('/api/data-files/list')                          # 数据文件列表
@app.route('/api/pm2/status')                               # PM2服务状态
```

---

## 🔍 故障排查

### 常见问题1：Flask启动失败
```bash
# 检查端口占用
lsof -i :9002

# 查看Flask日志
pm2 logs flask-app --lines 100

# 手动启动测试
cd /home/user/webapp
source venv/bin/activate
python3 app.py
```

### 常见问题2：采集器无数据
```bash
# 检查数据目录权限
ls -lh /home/user/webapp/data/

# 查看采集器日志
pm2 logs signal-collector --lines 50

# 手动执行采集器
cd /home/user/webapp
source venv/bin/activate
python3 source_code/signal_collector.py
```

### 常见问题3：PM2服务停止
```bash
# 查看所有服务状态
pm2 status

# 重启单个服务
pm2 restart flask-app

# 重启所有服务
pm2 restart all

# 删除所有服务并重新加载
pm2 delete all
pm2 start ecosystem.config.js
```

### 常见问题4：止盈止损不工作
```bash
# 1. 检查服务是否运行
pm2 list | grep okx-tpsl-monitor

# 2. 查看日志
pm2 logs okx-tpsl-monitor --lines 30

# 3. 检查API凭证
cat /home/user/webapp/data/okx_auto_strategy/account_main.json | jq

# 4. 重启服务
pm2 restart okx-tpsl-monitor
```

---

## 📝 部署检查清单

### ✅ 部署前检查
- [ ] 系统包已安装（Python, Node.js, PM2）
- [ ] 备份文件已下载（~2GB）
- [ ] 磁盘空间充足（至少10GB）
- [ ] 端口9002未被占用

### ✅ 部署中检查
- [ ] 备份文件已解压
- [ ] Python虚拟环境已创建
- [ ] 依赖包已安装（requirements.txt）
- [ ] PM2配置已加载（ecosystem.config.js）

### ✅ 部署后检查
- [ ] Flask应用正常运行（http://localhost:9002）
- [ ] PM2服务列表显示31个online
- [ ] 数据目录包含历史数据（~2GB）
- [ ] API端点返回正常
- [ ] Web界面可访问

---

## 🎯 性能优化建议

### 1. 数据库优化
- 当前使用JSONL文件存储（简单、灵活）
- 未来可考虑迁移到PostgreSQL或MongoDB（更快查询）

### 2. 缓存优化
- 添加Redis缓存高频数据
- 减少文件I/O操作

### 3. 并发优化
- Flask使用Gunicorn多进程部署
- PM2采集器增加并发实例

### 4. 监控优化
- 添加Prometheus + Grafana监控
- PM2 Monitoring仪表板

---

## 📞 技术支持

### 日志位置
```
PM2日志：/home/user/.pm2/logs/
Flask日志：控制台输出（pm2 logs flask-app）
数据文件：/home/user/webapp/data/
```

### 命令速查
```bash
# 查看所有服务
pm2 list

# 查看服务日志
pm2 logs [服务名] --lines 50

# 重启服务
pm2 restart [服务名]

# 保存PM2配置
pm2 save

# 删除服务
pm2 delete [服务名]
```

---

## 🔖 版本信息

**备份创建时间**：2026-02-17 14:59:00 UTC  
**系统版本**：v2.6  
**Git Commit**：f092ce4  
**备份大小**：~2GB（压缩后500-800MB）  
**包含数据**：全部历史数据（非7天）

---

**部署预计时间**：30-40分钟（含下载备份）  
**难度等级**：⭐⭐⭐ 中等（需要基本Linux和Python知识）

