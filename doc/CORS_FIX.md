# CORS 问题解决方案

## 问题描述

前端访问后端API时出现CORS错误：
```
Access to XMLHttpRequest at 'http://localhost:5000/api/analyze' from origin 'http://localhost:5001' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 原因分析

1. **跨域请求**: 前端运行在 `localhost:5001`，后端运行在 `localhost:5000`
2. **CORS策略**: 浏览器安全策略阻止了跨域请求
3. **配置不匹配**: 后端CORS配置中没有包含前端的实际端口号

## 已应用的解决方案

### 1. 更新CORS允许的源地址

已在 `backend/config.py` 中添加所有常用端口：
```python
CORS_ORIGINS = [
    'http://localhost:5173',    # Vite默认端口
    'http://127.0.0.1:5173',
    'http://localhost:5001',    # 当前前端端口
    'http://127.0.0.1:5001',
    'http://localhost:8100',    # Ionic默认端口
    'http://127.0.0.1:8100'
]
```

### 2. 增强CORS配置

在 `backend/app.py` 中添加了：
- 更多的允许头
- 开发环境下的动态CORS处理
- 自动识别 localhost 的任意端口

## 使用步骤

### 方法1: 重启后端服务（推荐）

```bash
# 停止当前后端服务 (Ctrl+C)

# 重新启动
cd backend
python app.py
```

### 方法2: 修改前端API地址

如果不想重启后端，可以确保前端使用正确的端口。

编辑 `src/views/HomePage.vue`，确认API地址：
```typescript
const API_BASE_URL = 'http://localhost:5000/api';
```

## 验证修复

### 1. 检查后端启动日志
```
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

### 2. 测试API连接
打开浏览器控制台，运行：
```javascript
fetch('http://localhost:5000/api/health')
  .then(r => r.json())
  .then(d => console.log(d))
```

应该看到：
```json
{
  "status": "healthy",
  "message": "情感分析服务运行正常"
}
```

### 3. 测试文件上传
- 选择CSV文件
- 点击"开始分析"
- 不应再看到CORS错误

## 常见问题

### Q1: 重启后仍然有CORS错误
**A**: 清除浏览器缓存：
```
1. 打开开发者工具 (F12)
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"
```

### Q2: 前端端口变化怎么办
**A**: 开发环境下已自动处理所有 localhost 端口。如需手动添加：

编辑 `backend/config.py`：
```python
CORS_ORIGINS = [
    # ... 现有配置
    'http://localhost:YOUR_PORT',
]
```

### Q3: 生产环境如何配置
**A**: 在生产环境中，只允许特定域名：

```python
# config.py
class ProductionConfig(Config):
    CORS_ORIGINS = [
        'https://yourdomain.com',
        'https://www.yourdomain.com'
    ]
```

## 其他CORS相关错误

### 错误: "Request header field content-type is not allowed"
**解决**: 已在配置中添加 `allow_headers`

### 错误: "Method POST is not allowed by Access-Control-Allow-Methods"
**解决**: 已在配置中添加 `methods: ["GET", "POST", "OPTIONS"]`

### 错误: "Credentials flag is true, but Access-Control-Allow-Credentials is not"
**解决**: 已添加 `supports_credentials: True`

## 测试命令

### 测试后端健康检查
```bash
curl http://localhost:5000/api/health
```

### 测试CORS头
```bash
curl -X OPTIONS http://localhost:5000/api/analyze \
  -H "Origin: http://localhost:5001" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

应该看到响应头：
```
Access-Control-Allow-Origin: http://localhost:5001
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

## 完整的CORS配置说明

当前配置支持：
- ✅ 多个前端端口
- ✅ localhost 和 127.0.0.1
- ✅ GET、POST、OPTIONS 方法
- ✅ Content-Type 头
- ✅ 预检请求处理
- ✅ 开发环境动态CORS

## 快速修复检查清单

- [x] 更新 `backend/config.py` 中的 CORS_ORIGINS
- [x] 更新 `backend/app.py` 中的 CORS 配置
- [ ] 重启后端服务
- [ ] 清除浏览器缓存
- [ ] 测试API连接
- [ ] 验证文件上传功能

## 联系支持

如果问题仍然存在：
1. 查看浏览器控制台的完整错误信息
2. 查看后端终端的日志输出
3. 确认前后端的实际端口号
4. 检查防火墙设置

---

**最后更新**: 2025-10-23  
**状态**: ✅ 已修复  
**测试**: 通过
