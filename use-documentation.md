# 用户手册

## 拿到这些代码你可以做什么

### 本地快速部署临时的群发系统

- 注释掉`server.py`中按用户过滤模板内容,可选
- `docker-compose up`
- `docker-compose exec server sh -c 'python databaseIO/databaseIO.py'` 快速创建用户 // TOUPGRADE
- 当然,config文件需要自己配置
- `python frontEnd_runme.py` 运行客户端

## 后端需要的config.json

```json
{
    "yunpian": {
        "apikey": "你的key"
    },
    "databaseIO": {
        "host": "172.18.0.1",
        "username": "用户名",
        "password": "密码",
        "db": "数据库",
        "port": 32769
    },
    "server_port": 29999,
    // 最新的客户端 版本号 以便提示更新
    "latest_qt_version": "1.0.0"
}
```

## 客户端需要的config.json

```json
{
    // 服务端地址
    "server_url":"http://localhost:29999",
    // 用户名
    "username":"网协",
    // 密码
    "password":"password"
}
```