<!-- 2018-06-29 10:32:41 -->
# 短信群发系统

# 项目名称
短信群发系统

# 项目技术栈
python3.6  qt-designer qt5
mysql

# 系统功能设定

短信群发系统分为前后端两个部分
- 前端
  - `登录自己的账号`
  - `上传excel`
  - 在GUI上修改信息（可选
  - 发送信息
  - 查询历史记录
  - 查询短信回复结果
- 后端
  - 监听各处的服务
  - 对账号进行验证，返回结果
  - 对数据库增删改查
  - 记录群发内容（证据留存）
  - 与外界api交互
  - 轮询外网获得反馈数据

## 后端处理逻辑

前端发送给后端的内容跟api格式几乎相同，不同的是
- 后端获取用户名密码，查询数据库，得到extend和uid，并加入data中
- 用户验证后加入apikey到data中
- 将构造好的信息发送给api
- 接受返回结果，（经处理后）返回给前端
- 将所有结果记录

## 后端数据库

- 权限 ： 
  - 客户端只有查询权限（防止注入
  - 账号的添加等操作需要网协手动处理


| 用户   | 权限    | 使用者   |
|------|-------|-------|
| --   | --    | --    |
| root | 完全    | 管理者界面 |
| user | 查询，修改 | 后端    |

- 权限设置语句

```sql
GRANT Select,UPDATE ON
 groupMessage.User TO user@'localhost' identified by "your-password" ;

 flush privileges;
```

- 表

`User`

| 列名        | 用途   | 数据类型          | 默认值  | 约束                          | 备注 |
|-----------|------|---------------|------|-----------------------------|----|
| id        | 唯一标识 | int(10)       |      | AUTO INCREAMENT PRIVATE KEY |    |
| username  | 用户信息 | varchar(30)   | NULL | NOT NULL                    |    |
| password  |      | char(32)      | NULL | NOTNULL                     |    |
| extend    | 区别用户 | int(10)       | NULL |                             |    |
| uid       | 区别用户 | int(10)       | NULL |                             |    |
| tplIDList | 模板id | varchar(1000) | ''   |                             |    |
createTime|该信息生成时间|DATETIME|CURRENT_TIMESTAMP	||该行插入时间
remark|备注信息|varchar(1000)||NOT NULL||



- 数据库生成语句

```sql
create database groupMessage 
CHARACTER SET 'utf8'
COLLATE 'utf8_general_ci';

use groupMessage;

create table User(
  id int(10) Primary key not null AUTO_INCREMENT ,
  username varchar(30) NOT NULL,
  password char(32) NOT NULL,
  extend int(10),
  uid int(10),
  tplIDList varchar(1000) DEFAULT '',
  createTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  remark varchar(1000) NOT NULL
)DEFAULT CHARSET=utf8;

-- 测试数据
insert into User(username,password,
extend,uid,
remark)
VALUE
('wangxie','md5',
0,01,'网络开拓者协会内部使用');
insert into User(username,password,
extend,uid,
remark)
VALUE
('shetuan1','md6',
0,02,'random group');
```
`数据库建立于2018-06-29 22:47:41测试通过`

## 后端完整逻辑

- 对前端
  - 监听端口
  - 对post请求做出响应
  - 应该提高性能？
- 内部
  - 处理数据，处理异常
  - 按照post请求的逻辑完成不同任务
    - 发送短信
    - 查询发送状态
    - 查询模板，并过滤
- 对数据库
  - 查询用户身份
- 对文件
  - 写入所有日志
- 外部
  - 向api发送请求
  - 接受结果

因此后端既是一个api server，也是数据库的执行者，也封装了api 的调用，还是日志记录的程序

## 项目进度

1. 2018-06-30
  - GUI 采用 QT 进行了初步学习，基本梳理了逻辑
  - api 研读了文档，进行测试，大致掌握方法
  - 后端 
    - 数据库 的设计已经完成，但是没有考虑`中间人`
    - httpserver 基本搭建成功，利用 http.server模块，使后端具有服务能力