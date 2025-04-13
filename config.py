import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # PostgreSQL 数据库配置
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = 5432
    POSTGRES_USER = 'luke'
    POSTGRES_PASSWORD = 'luke123'
    POSTGRES_DATABASE = 'crawlTable'
    
    # SQLAlchemy 配置
    SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API 配置
    API_PREFIX = '/api'
    JSON_AS_ASCII = False
    JSONIFY_MIMETYPE = 'application/json;charset=utf-8' 