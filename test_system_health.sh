#!/bin/bash

# OKX Trading System - 系统健康检查脚本
# 用于验证所有关键功能正常运行

echo "=========================================="
echo "OKX Trading System - 健康检查"
echo "检查时间: $(date)"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数
PASS=0
FAIL=0

# 函数: 检查API端点
check_api() {
    local endpoint=$1
    local description=$2
    
    echo -n "检查 $description ... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9002$endpoint 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $response)"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $response)"
        ((FAIL++))
        return 1
    fi
}

# 函数: 检查PM2进程
check_pm2_process() {
    local process_name=$1
    
    status=$(pm2 jlist 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for proc in data:
        if proc['name'] == '$process_name':
            print(proc['pm2_env']['status'])
            break
except:
    print('error')
" 2>/dev/null)
    
    if [ "$status" = "online" ]; then
        echo -e "${GREEN}✓${NC} $process_name"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗${NC} $process_name (状态: $status)"
        ((FAIL++))
        return 1
    fi
}

echo "========================================"
echo "1. PM2 进程状态检查"
echo "========================================"

pm2_processes=(
    "flask-app"
    "signal-collector"
    "liquidation-1h-collector"
    "crypto-index-collector"
    "okx-tpsl-monitor"
    "market-sentiment-collector"
    "price-position-collector"
)

for proc in "${pm2_processes[@]}"; do
    check_pm2_process "$proc"
done

echo ""
echo "========================================"
echo "2. Web 应用检查"
echo "========================================"

check_api "/" "主页"
check_api "/okx-trading-marks-v3" "OKX交易标记 V3"

echo ""
echo "========================================"
echo "3. API 端点检查"
echo "========================================"

check_api "/api/coin-change-tracker/latest" "币种变化追踪API"
check_api "/api/market-sentiment/latest" "市场情绪API"
check_api "/api/okx-trading/tpsl-settings/account_main" "OKX TPSL设置API"

echo ""
echo "========================================"
echo "4. 数据文件检查"
echo "========================================"

echo -n "检查 JSONL 数据文件 ... "
jsonl_count=$(find data -name "*.jsonl" -type f 2>/dev/null | wc -l)
if [ $jsonl_count -gt 0 ]; then
    echo -e "${GREEN}✓ 通过${NC} (找到 $jsonl_count 个文件)"
    ((PASS++))
else
    echo -e "${RED}✗ 失败${NC} (未找到JSONL文件)"
    ((FAIL++))
fi

echo -n "检查 配置文件 ... "
if [ -f ".env" ] && [ -f "okx_accounts.json" ] && [ -f "ecosystem.config.js" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ 失败${NC}"
    ((FAIL++))
fi

echo ""
echo "========================================"
echo "5. 日志检查"
echo "========================================"

echo -n "检查 日志目录 ... "
if [ -d "logs" ]; then
    log_count=$(ls -1 logs/*.log 2>/dev/null | wc -l)
    echo -e "${GREEN}✓ 通过${NC} ($log_count 个日志文件)"
    ((PASS++))
else
    echo -e "${RED}✗ 失败${NC}"
    ((FAIL++))
fi

echo ""
echo "========================================"
echo "检查摘要"
echo "========================================"
echo -e "通过: ${GREEN}$PASS${NC}"
echo -e "失败: ${RED}$FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！系统运行正常。${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  部分检查失败，请查看详细信息。${NC}"
    exit 1
fi
