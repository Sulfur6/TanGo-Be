# 项目简介

本项目为TanGo资源调度系统的后端框架

# 项目依赖

* Mysql 5.7.41
* Redis 7.0.9
* Python 需要安装3.8+版本
* Python 依赖在requirements.txt中

# 环境配置

Redis 还没用起来，可以暂时不装。

Mysql 要装，连接相关配置在core.settings当中，5.7+就够用。

## 创建虚拟环境

```
virtualenv venv
```

## 激活虚拟环境

```
source venv/bin/activate
```

如果用pycharm的话虚拟环境可以一键创建

## 安装依赖

```
pip3 install -r requirements.txt
```

# 启动项目

```angular2html
python main.py
```

当然也可以在pycharm里配置一个fastapi项目

## API文档

启动项目后，访问`http://<HOST>:<PORT>/docs`即可查看openapi文档，配合postman等调试工具可以更方便的调试。