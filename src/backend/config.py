"""
配置文件
"""
import os

class Config:
    """基础配置"""
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 文件上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'csv'}
    
    # CORS配置 - 添加所有可能的前端端口
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5001',
        'http://127.0.0.1:5001',
        'http://localhost:8100',  # Ionic默认端口
        'http://127.0.0.1:8100'
    ]
    
    # 分析配置
    DEFAULT_LANGUAGE = 'zh'
    DEFAULT_FEATURES = ['basic', 'sentiment_dict']
    
    # 模型配置
    POSITIVE_THRESHOLD = 0.6
    NEGATIVE_THRESHOLD = 0.4

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
