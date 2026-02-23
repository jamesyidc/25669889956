# 项目备份清单

## 备份信息

**备份日期**: 2026-02-23 11:40:00 UTC  
**备份文件**: `/tmp/webapp_full_backup_20260223.tar.gz`  
**备份大小**: 477MB (压缩后)  
**原始大小**: ~6.3GB  
**压缩率**: ~92.4%  
**文件数量**: 6,064个文件/目录

---

## 备份内容

### ✅ 包含的内容

1. **源代码** (~10MB)
   - ✅ Python文件 (app.py, 采集器, 管理器, 工具等)
   - ✅ HTML模板 (templates/)
   - ✅ JavaScript配置
   - ✅ CSS样式文件

2. **历史数据** (~800MB，已压缩)
   - ✅ data/coin_changes/ - 币种涨跌幅历史数据（全部）
   - ✅ data/market_sentiment/ - 市场情绪历史数据（全部）
   - ✅ data/daily_predictions/ - 日常预判历史数据（全部）
   - ✅ data/intraday_patterns/ - 日内模式检测数据（全部）
   - ✅ data/okx_trading_logs/ - OKX交易日志（全部）
   - ✅ data/wave_peaks/ - 波峰历史数据（全部）
   - ✅ data/favorite_symbols.jsonl - 收藏币种配置

3. **依赖环境**
   - ✅ venv/ - Python虚拟环境（~900MB，已压缩）
   - ✅ node_modules/ - Node.js依赖（~200MB，已压缩）
   - ✅ requirements.txt - Python依赖清单
   - ✅ package.json - Node.js依赖清单

4. **配置文件**
   - ✅ ecosystem.config.js - PM2进程管理配置
   - ✅ DEPLOYMENT_GUIDE.md - 部署指南
   - ⚠️ .env - 环境变量（需重新配置API密钥）

### ❌ 不包含的内容（已排除）

1. **临时文件**
   - ❌ logs/*.log - 日志文件（可重新生成）
   - ❌ *.pyc - Python字节码
   - ❌ __pycache__/ - Python缓存目录
   - ❌ .git/ - Git仓库（使用GitHub托管）

---

## 恢复步骤

### 快速恢复（推荐）

```bash
# 1. 解压备份
cd /home/user
tar -xzf /tmp/webapp_full_backup_20260223.tar.gz

# 2. 进入项目目录
cd webapp

# 3. 配置环境变量（重要！）
nano .env  # 填入OKX API密钥和Telegram配置

# 4. 激活Python环境
source venv/bin/activate

# 5. 启动应用
pm2 start ecosystem.config.js

# 6. 验证
curl http://localhost:9002/
pm2 logs
```

### 详细恢复（完整步骤）

参见 `DEPLOYMENT_GUIDE.md` 文档

---

## 数据验证

### 验证备份完整性

```bash
# 测试备份文件是否损坏
tar -tzf /tmp/webapp_full_backup_20260223.tar.gz > /dev/null
echo $?  # 应输出 0（成功）

# 查看备份内容
tar -tzf /tmp/webapp_full_backup_20260223.tar.gz | less

# 提取特定文件
tar -xzf /tmp/webapp_full_backup_20260223.tar.gz webapp/app.py
```

### 验证数据完整性

恢复后检查：

```bash
cd /home/user/webapp

# 检查数据目录
ls -lh data/
du -sh data/*

# 检查数据文件数量
find data/ -name "*.jsonl" | wc -l  # 应有数千个文件

# 检查最新数据
ls -lt data/coin_changes/ | head -5
ls -lt data/okx_trading_logs/ | head -5
```

---

## 关键依赖清单

### Python依赖

```
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
python-telegram-bot==20.5
pandas==2.1.0
cryptography==41.0.3
```

### Node.js依赖

```json
{
  "pm2": "^5.3.0",
  "express": "^4.18.2"
}
```

### 系统依赖

```
python3 (3.8+)
nodejs (18+)
npm (9+)
pm2 (全局安装)
```

---

## 备份文件位置

**主备份**:  
`/tmp/webapp_full_backup_20260223.tar.gz` (477MB)

**备份日志**:  
`/tmp/backup_log_20260223_*.txt`

**部署文档**:  
`/home/user/webapp/DEPLOYMENT_GUIDE.md`

---

## 注意事项

⚠️ **重要提醒**:

1. **环境变量**: `.env` 文件需重新配置API密钥
2. **端口检查**: 确保端口9002未被占用
3. **Python版本**: 需要Python 3.8或更高版本
4. **Node版本**: 需要Node.js 18或更高版本
5. **权限设置**: 确保数据目录可读写
6. **PM2安装**: 需要全局安装pm2 (`npm install -g pm2`)

---

## 技术支持

**Git仓库**: https://github.com/jamesyidc/25669889956  
**分支**: restored-from-backup  
**最新提交**: 66ea1aa (docs: 添加完整部署指南)

**问题反馈**:  
如恢复过程中遇到问题，请查看：
- DEPLOYMENT_GUIDE.md - 完整部署指南
- /tmp/backup_log_*.txt - 备份日志
- pm2 logs - 应用运行日志

---

**文档版本**: 1.0  
**创建日期**: 2026-02-23  
**备份工具版本**: v1.0
