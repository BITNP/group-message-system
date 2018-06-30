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
- 目前开发的功能
  - 单条发送
  - 批量模板群发
  - 接受推送回复短信
  - 按用户添加，查询，修改，删除模板
  - 查看当前使用费用

## 后端处理逻辑

前端发送给后端的内容跟api格式几乎相同，不同的是
- 后端获取用户名密码，查询数据库，得到extend和uid，并加入data中
- 用户验证后加入apikey到data中
- 将构造好的信息发送给api
- 接受返回结果，（经处理后）返回给前端
- 将所有结果记录

## 后端数据库

- 权限 ： 
  - 客户端只有查询和插入和更改的权限（防止注入
  - 账号的添加等操作需要网协手动处理


| 用户   | 权限       | 使用者   |
|------|----------|-------|
| --   | --       | --    |
| root | 完全       | 管理者界面 |
| user | 查询，修改，插入 | 后端    |

- 逻辑

用户表存放着用户相关信息，方便后端区分用户。
每个用户又拥有一个发送记录表，和群发信息表。
短信的具体内容都存在前者；如果是群发，则后者存放所有对应手机号和发送情况，并存储回复情况
extend 就是用户的主键，
uid 是每次的id，就是第二个表的主键


- 权限设置语句

```sql
GRANT Select,UPDATE ON
 groupMessage.* TO user@'localhost' identified by "your-password" ;
 -- 为啥docker的话不能用localhost？下面是docker的地址
 GRANT Select,UPDATE ON
 groupMessage.* TO user@'172.17.0.1' identified by "your-password" ;

 flush privileges;
```

- 表

`User`

| 列名         | 用途      | 数据类型          | 默认值               | 约束                          | 备注          |
|------------|---------|---------------|-------------------|-----------------------------|-------------|
| id         | 唯一标识    | BIGINT        |                   | AUTO INCREAMENT PRIMARY KEY | 就当做extend值？ |
| username   | 用户信息    | varchar(45)   | NULL              | NOT NULL                    |             |
| password   |         | char(32)      | NULL              | NOT NULL                    |             |
| fee        | 总计花费    | DECIMAL(10,2) | 0                 | NOT NULL                    |             |
| tplIDList  | 模板id    | varchar(1000) | ''                |                             |             |
| fee        | 总花费       | DECIMAL(10,2) | 0.0               | NOT NULL                    |                |
| paid       | 已缴费        | DECIMAL(10,2) | 0.0               | NOT NULL                    |                |
| createTime | 该信息生成时间 | DATETIME      | CURRENT_TIMESTAMP |                             |             |
| remark     | 备注信息    | varchar(1000) |                   | NOT NULL                    |             |

`SendStat`
| 列名         | 用途         | 数据类型          | 默认值               | 约束                          | 备注             |
|------------|------------|---------------|-------------------|-----------------------------|----------------|
| mid        | 唯一标识       | INT           |                   | AUTO INCREAMENT PRIMARY KEY | 仅在数据库中使用       |
| id         | 区分用户       | INT           |                   | NOT NULL 外键约束               | User表中id       |
| uid        | 区分批次       | INT           |   NULL     |     NOT NULL                  | GroupData 中 使用 |
| createTime | 生成时间       | DATETIME      | CURRENT_TIMESTAMP |                             |                |
| content    | 短信内容       | text(1000)    |                   |                             |                |
| fee        | 这次花费       | DECIMAL(10,2) | 0.0               | NOT NULL                    |                |
| count      | 计数         | INT           | 1                 |                             |                |
| mobile     | 单个发送中的手机号  | char(11)      |                   |                             |                |
| sid        | 单个发送中的sid  | BIGINT        |                   |                             | 来自api          |
| code       | 单个发送中的发送状态 | int           |                   |                             |                |
| msg        | 单个发送中的信息   | varchar(500)  |                   |                             |                |

`GroupData`

| 列名     | 用途       | 数据类型          | 默认值  | 约束              | 备注        |
|--------|----------|---------------|------|-----------------|-----------|
| sid    | 唯一标识     | BIGINT        |      | PRIMARY KEY     | 与api返回值相同 |
| id     | 区分用户     | INT           |      | NOT NULL 外键约束   | User表中id  |
| uid    | 表示分类     | INT           |      | NOT NULL   外键约束 | 来自上文      |
| mobile | 手机号      |               |      |                 |           |
| code   | 发送状态     | INT           | NULL |                 | 与api返回值相同 |
| fee    | 费用       | DECIMAL(10,2) |      |                 |           |
| msg    | 单个发送中的信息 | varchar(500)  |      |                 |           |

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
  fee DECIMAL(10,2) DEFAULT 0,
  tplIDList varchar(1000) DEFAULT '',
  createTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  remark varchar(1000) NOT NULL
)DEFAULT CHARSET=utf8;


create table User(
  uid INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  createTime 
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

## 前端->后端 api 用`request_code`字段

| 值   | 含义       | 后端需要做的处理                                            |                        |
|-----|----------|-----------------------------------------------------|------------------------|
| 1   | 单条发送     | `https://sms.yunpian.com/v2/sms/single_send.json`   | uid,extend,mobile,text |
| 2.1 | 获取默认模板   |                                                     |                        |
| 2.2 | 获取模板     | `https://sms.yunpian.com/v2/tpl/get.json`           |                        |
| 2.3 | 添加模版     | `https://sms.yunpian.com/v2/tpl/add.json`           |                        |
| 2.4 | 修改模板     |                                                     |                        |
| 2.5 | 删除模板     |                                                     |                        |
| 3.1 | 添加签名     |                                                     |                        |
| 3.2 | 获取签名     |                                                     |                        |
| 3.3 | 修改签名     |                                                     |                        |
| 4   | 查看短信发送记录 |                                                     |                        |
| 7   | 日账单导出    | `https://sms.yunpian.com/v2/sms/get_total_fee.json` |                        |

## 一些注意事项

- 传送中文时要指明使用`.encode('utf-8')`
- 若传入是json但是不是字典呢？

## 项目进度

- 2018-06-29
  - GUI 采用 QT 进行了初步学习，基本梳理了逻辑
  - api 研读了文档，进行测试，大致掌握方法
  - 后端
    - 数据库 的设计已经完成，但是还没有考虑`中间人`安全问题
    - httpserver 基本搭建成功，利用 http.server模块，使后端具有服务能力
- 2018-06-30
  - 加入数据库验证
  - 后端基本逻辑完成
