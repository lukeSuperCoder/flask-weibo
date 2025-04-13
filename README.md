# Flask API 服务

这是一个使用 Flask 框架搭建的 RESTful API 服务。

## 功能特点

- 支持跨域请求（CORS）
- 统一的 JSON 响应格式
- 错误处理机制
- 配置管理
- 环境变量支持

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python app.py
```

服务将在 http://localhost:5000 启动

## 示例接口

- GET /api/hello - 返回欢迎信息

## 项目结构

```
.
├── app.py          # 主应用文件
├── config.py       # 配置文件
├── requirements.txt # 项目依赖
└── README.md       # 项目说明
``` 