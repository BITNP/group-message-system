# 用户手册

## 拿到这些代码你可以做什么

### 本地快速部署临时的群发系统

- 注释掉`server.py`中按用户过滤模板内容,可选
- `docker-compose up`
- `docker-compose exec server sh -c 'python databaseIO/databaseIO.py'` 快速创建用户 // TOUPGRADE
- 当然,config文件需要自己配置
- `python frontEnd_runme.py` 运行客户端