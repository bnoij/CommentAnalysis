<!-- @format -->

# 项目部署指南

## 系统要求

### 软件要求

-   **Python**: 3.8 或更高版本
-   **Node.js**: 16.0 或更高版本
-   **npm**: 8.0 或更高版本

### 操作系统

-   Windows 10/11
-   macOS 10.15+
-   Linux (Ubuntu 20.04+, CentOS 8+)

## 安装步骤

### 方法一: 使用自动脚本(推荐)

#### Windows

```cmd
# 双击运行
start.bat
```

#### Linux/Mac

```bash
chmod +x start.sh
./start.sh
```

### 方法二: 手动安装

#### 1. 克隆项目

```bash
git clone <repository-url>
cd snownlp
```

#### 2. 后端安装

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 测试后端
python test.py

# 启动服务
python app.py
```

#### 3. 前端安装

```bash
# 返回项目根目录
cd ..

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 配置说明

### 后端配置

编辑 `backend/config.py`:

```python
class Config:
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 修改文件大小限制

    # CORS配置
    CORS_ORIGINS = ['http://localhost:5173']  # 添加允许的源

    # 模型配置
    POSITIVE_THRESHOLD = 0.6  # 调整正面阈值
    NEGATIVE_THRESHOLD = 0.4  # 调整负面阈值
```

### 前端配置

编辑 `src/views/HomePage.vue`:

```typescript
// 修改API地址
const API_BASE_URL = "http://localhost:5000/api";
```

## 生产环境部署

### 后端部署

#### 使用 Gunicorn (推荐)

1. 安装 Gunicorn:

```bash
pip install gunicorn
```

2. 启动服务:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 使用 uWSGI

1. 安装 uWSGI:

```bash
pip install uwsgi
```

2. 创建 `uwsgi.ini`:

```ini
[uwsgi]
module = app:app
master = true
processes = 4
socket = 0.0.0.0:5000
chmod-socket = 660
vacuum = true
die-on-term = true
```

3. 启动:

```bash
uwsgi --ini uwsgi.ini
```

### 前端部署

#### 构建生产版本

```bash
npm run build
```

生成的文件在 `dist/` 目录

#### 使用 Nginx 部署

1. 安装 Nginx

2. 配置文件 `/etc/nginx/sites-available/sentiment-analysis`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/snownlp/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. 启用站点:

```bash
sudo ln -s /etc/nginx/sites-available/sentiment-analysis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker 部署

### 创建 Dockerfile (后端)

`backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### 创建 Dockerfile (前端)

`Dockerfile`:

```dockerfile
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

`docker-compose.yml`:

```yaml
version: "3.8"

services:
    backend:
        build: ./backend
        ports:
            - "5000:5000"
        volumes:
            - ./backend:/app
        environment:
            - FLASK_ENV=production

    frontend:
        build: .
        ports:
            - "80:80"
        depends_on:
            - backend
```

启动:

```bash
docker-compose up -d
```

## 性能优化

### 后端优化

1. **启用缓存**:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)
def analyze_sentiment():
    # ...
```

2. **数据库存储结果**:
   使用 SQLite 或 PostgreSQL 存储分析历史

3. **异步处理**:
   对于大文件使用 Celery 进行后台处理

### 前端优化

1. **启用压缩**:

```bash
npm run build -- --mode production
```

2. **CDN 加速**:
   将静态资源上传到 CDN

3. **懒加载**:
   按需加载组件和图表

## 监控和日志

### 后端日志

添加日志配置:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 监控工具

-   **Prometheus + Grafana**: 系统监控
-   **Sentry**: 错误追踪
-   **ELK Stack**: 日志分析

## 安全建议

1. **API 密钥认证**:

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != app.config['API_KEY']:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated
```

2. **限流**:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@limiter.limit("10 per minute")
def analyze_sentiment():
    # ...
```

3. **HTTPS 部署**:
   使用 Let's Encrypt 获取免费 SSL 证书

4. **输入验证**:
   严格验证上传文件的内容和格式

## 备份策略

1. **定期备份数据**:

```bash
# 备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup-$DATE.tar.gz backend/uploads backend/*.db
```

2. **版本控制**:
   使用 Git 管理代码版本

3. **数据库备份**:
   定期导出分析结果

## 故障排除

### 常见问题

1. **端口被占用**:

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

2. **依赖安装失败**:

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
npm install --registry=https://registry.npmmirror.com
```

3. **内存不足**:

-   减少 worker 数量
-   限制并发请求
-   增加服务器内存

## 升级指南

### 更新依赖

```bash
# 后端
pip install --upgrade -r requirements.txt

# 前端
npm update
```

### 数据迁移

如果模型或数据结构变化,需要:

1. 备份现有数据
2. 运行迁移脚本
3. 验证数据完整性

## 联系支持

遇到问题请:

1. 查看文档和 FAQ
2. 检查日志文件
3. 提交 Issue 到 GitHub

## 许可证

本项目采用 MIT 许可证
