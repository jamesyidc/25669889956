# 🎯 开关保存功能验证指南

## ✅ 功能状态

**后端**: ✅ 正常工作，已验证  
**前端**: ✅ 代码完整，已部署  
**测试**: ✅ API测试通过

---

## 🔍 功能验证步骤

### 步骤 1: 清除浏览器缓存

**非常重要！** 旧的JS缓存可能导致新功能无法生效。

**操作方法**：
1. 打开页面：https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/okx-trading
2. 按 **Ctrl+Shift+R** (Windows) 或 **Cmd+Shift+R** (macOS) **强制刷新**
3. 或者按 **Ctrl+Shift+Delete** 打开"清除浏览数据"，选择"缓存的图片和文件"

---

### 步骤 2: 打开浏览器控制台

按 **F12** 打开开发者工具，切换到 **Console** 标签。

---

### 步骤 3: 测试开关保存

1. **选择账户**：点击左侧的 `account_main` 账户标签

2. **输入阈值**：在"止盈管理"输入框输入 `50`

3. **打开开关**：点击"止盈管理"旁边的开关

4. **查看结果**：
   - ✅ **控制台日志**：
     ```
     🔄 [saveSingleSwitch] 字段=takeProfitEnabled, 新值=true
     ✅ [saveSingleSwitch] takeProfitEnabled 已保存为 true
     📝 已记录止盈设置变更到策略日志: 启用
     ```
   
   - ✅ **Toast 通知**：
     - 页面右上角出现绿色卡片
     - 消息：`✅ 止盈设置已保存：已启用，阈值 50 USDT`
     - 3秒后自动消失

5. **验证保存**：
   - 刷新页面（Ctrl+Shift+R）
   - 开关应该保持打开状态
   - 阈值应该保持为 50

---

### 步骤 4: 测试多个开关

1. **打开止损开关**：
   - 输入 `-30`
   - 点击开关
   - 应该看到 Toast：`✅ 止损设置已保存：已启用，阈值 -30 USDT`

2. **打开 RSI 多单止盈**：
   - 输入 `1900`
   - 点击开关
   - 应该看到 Toast：`✅ RSI多单止盈已保存：已启用，阈值 1900`

3. **验证所有开关**：
   - 刷新页面
   - 所有3个开关应该都保持打开状态

---

## 🐛 故障排查

### 问题 1: 没有看到 Toast 通知

**可能原因**：
1. 浏览器缓存未清除
2. JavaScript 错误

**解决方法**：
1. 按 Ctrl+Shift+R 强制刷新
2. 打开控制台（F12），查看是否有红色错误信息
3. 在控制台输入：`typeof showSuccessToast`，应该返回 `"function"`
4. 手动测试 Toast：在控制台输入 `showSuccessToast("测试消息")`，应该在右上角看到绿色卡片

---

### 问题 2: 开关没有保存

**可能原因**：
1. 未选择账户
2. 网络请求失败

**解决方法**：
1. 确认左侧账户标签是蓝色高亮状态
2. 打开控制台，查看是否有 `❌` 红色错误
3. 检查网络请求：
   - 切换到 **Network** 标签
   - 点击开关
   - 查找 `/api/okx-trading/tpsl-settings/account_main` 请求
   - 应该返回 `200 OK` 和 `{success: true}`

---

### 问题 3: 刷新后开关状态恢复

**可能原因**：
保存失败，但没有显示错误

**解决方法**：
1. 打开控制台
2. 点击开关
3. 查看是否有以下日志：
   ```
   ✅ [saveSingleSwitch] takeProfitEnabled 已保存为 true
   ```
4. 如果看到 `❌` 错误，截图发送给开发人员

---

## 🧪 手动API测试

如果前端无法使用，可以用命令行测试后端：

```bash
# 打开止盈开关
curl -X POST http://localhost:9002/api/okx-trading/tpsl-settings/account_main \
  -H "Content-Type: application/json" \
  -d '{
    "takeProfitEnabled": true,
    "takeProfitThreshold": 50,
    "stopLossEnabled": false,
    "stopLossThreshold": -30,
    "rsiTakeProfitEnabled": false,
    "rsiTakeProfitThreshold": 1900,
    "rsiShortTakeProfitEnabled": false,
    "rsiShortTakeProfitThreshold": 810,
    "sentimentTakeProfitEnabled": false,
    "maxPositionValueUsdt": 5.0
  }'

# 查看当前设置
curl http://localhost:9002/api/okx-trading/tpsl-settings/account_main

# 查看 JSONL 文件
tail -1 /home/user/webapp/data/okx_tpsl_settings/account_main_tpsl.jsonl | python3 -m json.tool
```

---

## 📊 验证结果

### ✅ 后端验证（已完成）

```bash
# 测试结果
{
  "success": true,
  "message": "止盈止损设置已保存到JSONL",
  "settings": {
    "takeProfitEnabled": true,  ✅
    "takeProfitThreshold": 50.0  ✅
  }
}

# JSONL 文件验证
{
  "take_profit_enabled": true,  ✅
  "take_profit_threshold": 50.0,  ✅
  "last_updated": "2026-02-21 09:16:58"  ✅
}
```

---

## 🎬 视频演示步骤

如果仍然无法使用，请录屏操作过程：

1. 打开页面
2. 按 F12 打开控制台
3. 按 Ctrl+Shift+R 刷新页面
4. 选择账户
5. 点击开关
6. 显示控制台日志和页面右上角

发送录屏给开发人员分析。

---

## 📞 联系支持

如果以上步骤都无法解决问题，请提供：

1. **浏览器信息**：Chrome / Firefox / Safari，版本号
2. **控制台截图**：包括所有日志和错误
3. **网络请求截图**：Network 标签的请求/响应
4. **操作录屏**：完整的操作过程

---

**最后更新**: 2026-02-21 09:17 (北京时间)  
**文件版本**: v1.0  
**状态**: ✅ 后端已验证，前端代码已部署
