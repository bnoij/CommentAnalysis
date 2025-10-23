<!-- @format -->

# 问题排查指南

## 🔍 当前问题: CORS 错误

### 错误信息

```
Access to XMLHttpRequest at 'http://localhost:5000/api/analyze' from origin 'http://localhost:5001'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### ✅ 已应用的修复

1. **更新了 CORS 配置** (`backend/config.py`)

    - 添加了 `http://localhost:5001` 到允许列表
    - 添加了其他常用端口 (5173, 8100)

2. **增强了 CORS 处理** (`backend/app.py`)

    - 添加了开发环境下的动态 CORS 支持
    - 自动允许所有 localhost 端口

3. **改进了错误提示** (`src/views/HomePage.vue`)
    - 添加了更详细的错误信息
    - 区分网络错误和服务器错误

## 🚀 立即解决步骤

### 步骤 1: 重启后端服务 ⭐⭐⭐

**这是最重要的步骤!** 配置更改需要重启服务才能生效。

```bash
# 在后端终端中:
# 1. 按 Ctrl+C 停止当前服务
# 2. 重新启动

cd backend
python app.py
```

看到以下输出说明启动成功:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

### 步骤 2: 清除浏览器缓存

浏览器可能缓存了旧的 CORS 响应。

**Chrome/Edge:**

1. 按 F12 打开开发者工具
2. 右键点击刷新按钮
3. 选择 "清空缓存并硬性重新加载"

**或者:**

1. 按 Ctrl+Shift+Delete
2. 选择 "缓存的图像和文件"
3. 点击 "清除数据"

### 步骤 3: 测试连接

打开浏览器控制台 (F12)，运行:

```javascript
// 测试后端是否可访问
fetch("http://localhost:5000/api/health")
    .then((r) => r.json())
    .then((d) => console.log("✓ 后端正常:", d))
    .catch((e) =>
        console.error("✗ 后端错误:", e)
    );
```

### 步骤 4: 重新尝试分析

1. 刷新前端页面 (F5)
2. 选择 CSV 文件
3. 配置参数
4. 点击"开始分析"

## 🧪 验证修复

### 方法 1: 运行 CORS 测试脚本

```bash
cd backend
python test_cors.py
```

应该看到所有 ✓ 标记。

### 方法 2: 手动测试 API

```bash
# 测试健康检查
curl http://localhost:5000/api/health

# 测试CORS预检
curl -X OPTIONS http://localhost:5000/api/analyze \
  -H "Origin: http://localhost:5001" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

在响应中应该看到:

```
< Access-Control-Allow-Origin: http://localhost:5001
< Access-Control-Allow-Methods: GET, POST, OPTIONS
```

## 📋 完整检查清单

运行以下检查，确保所有步骤都完成:

-   [ ] **文件已更新**

    -   [x] `backend/config.py` - CORS_ORIGINS 包含 5001 端口
    -   [x] `backend/app.py` - 添加了开发环境 CORS 处理
    -   [x] `src/views/HomePage.vue` - 改进了错误处理

-   [ ] **服务状态**

    -   [ ] 后端服务已重启
    -   [ ] 后端运行在 5000 端口
    -   [ ] 前端运行在 5001 端口
    -   [ ] 可以访问 http://localhost:5000/api/health

-   [ ] **浏览器设置**

    -   [ ] 已清除缓存
    -   [ ] 已刷新页面
    -   [ ] 开发者工具已打开 (查看错误)

-   [ ] **测试**
    -   [ ] API 健康检查返回正常
    -   [ ] CORS 测试脚本全部通过
    -   [ ] 文件上传不再报 CORS 错误

## 🐛 如果问题仍然存在

### 情况 1: 仍然看到 CORS 错误

**检查后端日志:**

-   请求是否到达后端? (应该看到 POST /api/analyze)
-   响应状态码是什么? (应该是 200)

**解决方案:**

```python
# 在 backend/app.py 的开头添加调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

@app.before_request
def log_request():
    app.logger.debug(f'Request: {request.method} {request.path}')
    app.logger.debug(f'Origin: {request.headers.get("Origin")}')
```

### 情况 2: 后端无法启动

**检查端口占用:**

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5000
kill -9 <PID>
```

**检查依赖:**

```bash
cd backend
pip list | grep -E "(Flask|flask-cors)"
```

应该看到:

```
Flask          3.0.0
Flask-Cors     4.0.0
```

### 情况 3: 前端端口改变

如果前端运行在不同端口 (如 5173):

**选项 A: 更新配置文件**

```python
# backend/config.py
CORS_ORIGINS = [
    'http://localhost:YOUR_NEW_PORT',
    # ...
]
```

**选项 B: 使用通配符 (仅开发)**

```python
# backend/app.py (已包含)
# 开发环境会自动允许所有 localhost 端口
```

### 情况 4: 防火墙阻止

**Windows:**

```powershell
# 允许Python通过防火墙
New-NetFirewallRule -DisplayName "Python" -Direction Inbound -Program "C:\Path\To\python.exe" -Action Allow
```

**Mac:**

```bash
# 系统偏好设置 > 安全性与隐私 > 防火墙 > 防火墙选项
# 允许Python接入连接
```

## 🔧 临时解决方案

如果需要立即测试，可以使用以下临时方案:

### 方案 1: 使用代理

在 `vite.config.ts` 中添加代理:

```typescript
export default defineConfig({
    server: {
        proxy: {
            "/api": {
                target: "http://localhost:5000",
                changeOrigin: true,
            },
        },
    },
});
```

然后修改前端 API 地址:

```typescript
const API_BASE_URL = "/api";
```

### 方案 2: 禁用浏览器 CORS (不推荐)

**Chrome:**

```bash
chrome.exe --disable-web-security --user-data-dir="C:/ChromeDevSession"
```

⚠️ **警告**: 仅用于开发测试，关闭后不要浏览其他网站!

## 📞 获取帮助

如果以上方法都无效:

1. **收集信息:**

    - 浏览器控制台完整错误信息
    - 后端终端日志
    - 运行 `python test_cors.py` 的输出
    - 前端实际运行端口
    - 后端实际运行端口

2. **检查配置:**

    ```bash
    # 查看当前配置
    cd backend
    python -c "from config import config; print(config['development'].CORS_ORIGINS)"
    ```

3. **验证网络:**
    ```bash
    # 测试本地连接
    curl http://localhost:5000/api/health
    curl http://127.0.0.1:5000/api/health
    ```

## 📚 相关文档

-   [CORS_FIX.md](CORS_FIX.md) - CORS 问题详细说明
-   [USAGE.md](USAGE.md) - 完整使用指南
-   [DEVELOPER.md](DEVELOPER.md) - 开发者指南

## ✅ 成功标志

修复成功后，你应该看到:

1. ✅ 浏览器控制台没有 CORS 错误
2. ✅ 后端日志显示 `POST /api/analyze HTTP/1.1" 200`
3. ✅ 前端显示 "分析完成!" 的绿色提示
4. ✅ 结果正常显示在界面上

---

**最后更新**: 2025-10-23  
**问题**: CORS 跨域请求被阻止  
**状态**: ✅ 已提供解决方案  
**下一步**: 重启后端服务
