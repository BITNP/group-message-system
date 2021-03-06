<!-- 2018-06-29 10:32:41 -->
# 短信群发系统

## 项目名称

短信群发系统

## 项目技术栈

python3.6  qt-designer qt5
mysql

## 系统功能设定

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

- 权限
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
extend值长三位大概每学年要重新制零一次？
由于对于业务的了解于`2018-07-01`又深了一些，所以数据库可能要重新设计
尤其是只用extend区别流水，这跟之前计划的不太一样

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
| username   | 用户信息    | varchar(45)   | NULL              | NOT NULL UQ                 |             |
| password   |         | char(32)      | NULL              | NOT NULL                    |             |
| fee        | 总记花费    | DECIMAL(10,2) | 0.0               | NOT NULL                    |             |
| paid       | 已缴费     | DECIMAL(10,2) | 0.0               | NOT NULL                    |             |
| createTime | 该信息生成时间 | DATETIME      | CURRENT_TIMESTAMP |                             |             |
| remark     | 备注信息    | varchar(1000) |                   | NOT NULL                    |             |

`SendStat`

| 列名         | 用途        | 数据类型          | 默认值               | 约束                           | 备注                                                 |
|------------|-----------|---------------|-------------------|------------------------------|----------------------------------------------------|
| extend     | 区分批次      | INT           | NULL              | PK NOT NULL   AUTO INCREMENT | GroupData 中使用，所有的用户共用一套自增的，等同于extend，另外，需要注意最多只有三位 |
| id         | 区分用户      | INT           |                   | NOT NULL 外键约束                | User表中id                                           |
| api        | 做厂商区分     | INT           |                   | NOT NULL                     | 1:yunpian,2:tencent                                |
| ext        | 保留        | char(32)      |                   |                              | 用户的 session 内容，腾讯 server 回包中会原样返回                  |
| createTime | 生成时间      | DATETIME      | CURRENT_TIMESTAMP |                              |                                                    |
| tpl_id     | 模板短信的模板id | BIGINT        |                   |                              |                                                    |
| content    | 短信内容      | varchar(500)  |                   |                              | 如果没有使用模板发送这个值必填                                    |
| fee        | 这次花费      | DECIMAL(10,2) | 0.0               | NOT NULL                     |                                                    |
| count      | 计数        | INT           | 1                 |                              | 后端统计发送的数量，与下面的对照                                   |
| totalCount | 计数        | INT           | 1                 |                              | api 返回的统计结果，只统计成功的                                 |

`GroupData`

| 列名         | 用途         | 数据类型          | 默认值               | 约束              | 备注                    |
|------------|------------|---------------|-------------------|-----------------|-----------------------|
| pid        | 唯一标识       | BIGINT        |                   | PRIMARY KEY  AI | 仅在数据库中使用              |
| sid        | 唯一标识       | char(32)      |                   |                 | 与api返回值相同             |
| id         | 区分用户       | INT           |                   | NOT NULL 外键约束   | User表中id              |
| extend     | 表示分类       | INT           |                   | NOT NULL   外键约束 | 来自上文                  |
| createTime | 创建时间       | DATETIME      | CURRENT_TIMESTAMP |                 |                       |
| param      | 群发参数       | text(500)     |                   |                 |                       |
| mobile     | 手机号        |               |                   |                 |                       |
| result     | 发送状态（计费依据） | INT           | NULL              |                 | 与api返回值相同 code/result |
| fee        | 费用         | DECIMAL(10,2) |                   |                 |                       |
| errmsg     | api回复的信息   | varchar(500)  |                   |                 |                       |
| reply      | 短信回复       | varchar(500)  |                   |                 | 空值则为没有回复              |

`Tpl`

| 列名         | 用途              | 数据类型         | 默认值               | 约束              | 备注                        |
|------------|-----------------|--------------|-------------------|-----------------|---------------------------|
| pid        | 唯一标识            | BIGINT       |                   | PRIMARY KEY  AI | 仅在数据库中使用                  |
| id         | 用户id            | INT          |                   |                 |                           |
| tpl_id     | 模板id            | BIGINT       |                   |                 |                           |
| public     | 是否为共用模板         | INT          | 0                 |                 |                           |
| api        | 自行定义，做不同厂商的模板区分 | INT          |                   | NOT NULL        | 1:yunpian,2:tencent 与接口相同 |
| createTime | 创建时间            | DATETIME     | CURRENT_TIMESTAMP |                 |                           |
| text       | 模板内容            | varchar(500) |                   | NOT NULL        |                           |
| title      | 模板名称            | varchar(200) |                   |                 |                           |
| remark     | 模板备注            | varchar(200) |                   |                 |                           |
| result     | 错误码             | INT          |                   |                 |                           |
| errmsg     |                 | varchar(100) |                   |                 | 错误消息，result 非 0 时的具体错误信息  |
| status     | 模板状态            | INT          |                   |                 | Enum{0：已通过, 1：待审核, 2：已拒绝} |

- 数据库生成语句

```sql
-- 采用workbench进行数据库设计
-- 所有生成语句保存在了单独文本中

```
`数据库建立于2018-06-29 22:47:41测试通过`
`数据库与2018-07-01 19:54:00重构`

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

| 值   | 含义       | api                                               | 后端需要做的处理 |
|-----|----------|---------------------------------------------------|----------|
| 1.1 | 获取默认模板   | `https://sms.yunpian.com/v2/tpl/get_default.json` | 不在客户端实现  |
| 1.2 | 获取可用模板   | `https://sms.yunpian.com/v2/tpl/get.json`         | 过滤       |
| 1.3 | 添加模版     | `https://sms.yunpian.com/v2/tpl/add.json`         | 模板格式     |
| 1.4 | 制定模板群发   | `https://sms.yunpian.com/v2/sms/multi_send.json`  |          |
| 1.5 | 查看短信发送记录 | `https://sms.yunpian.com/v2/sms/get_record.json`  | 不在客户端实现  |
| 2.1 | 获取默认模板   |                                                   | 不在客户端实现  |
| 2.2 | 获取可用模板   |                                                   | 过滤       |
| 2.3 | 添加模版     |                                                   | 模板格式     |
| 2.4 | 制定模板群发   |                                                   |          |
| 2.5 | 查看短信发送记录 |                                                   | 不在客户端实现  |
| 6   | 历史记录信息导出 | 服务端                                               |          |
| 7   | 账户信息导出   | 服务端                                               |          |

## 前后端接口格式

```json

{
  // POST 方法参数
  // 以下内容是 基础参数
  "username":"用户名",
  "password":"密码",
  "request_code":"区分请求，详见文档",
  // 以下内容是 发送短信 需要的参数
  "mobile":["1880***1234","1880***2234","1880***3234"], 
  "param":[["每一个电话对应一个列表"],[""],[""]],
  "replace":["记录需要替换的内容，与param的列数量一致"],
  "content":"模板内容，将替换，没有param参数则不替换",
  "tpl_id":"可选，与上面的选择其一",
  // 以下内容是 添加模板 需要的参数
  "tpl_content":"模板内容",
}

{
  // 当错误发生时，POST 返回信息；否则返回接口信息
  "code":1323, //错误码
  "msg":"错误信息"
}

{
  "total_count":3,
  "total_fee":1.40,
  "unit":"RMB",
  "data":[
    {
      "code":0,
      "msg":"发送成功",
      "count":1,
      "fee":0.05,
      "unit":"RMB",
      "mobile":"13000000000",
      "sid":2342342324
      // 注意 sid 并不唯一， 请不要用来做严格区分
    },
    {
      // ...
    }
  ]
}



{
  // GET方法返回信息
  "api":[
    "云片网",
    "腾讯" // 列表形式的可选服务，注意云片网实际对应1，腾讯对应2...
  ],
  "new_qt_version":"最新的客户端版本" // 用于比较提示
}



[// *.1 / *.2 返回信息
  {
    "tpl_id":123,
    "tpl_content":"具体内容",
    "check_status":"审核状态",
    "reason":"具体说明"
  },
  {
    // ...
  }
]

{  // *.3 的返回值，正确则只返回无内容的json
  "code":234,
  "msg":"参数传入格式有误"
}

{  // *.4 的返回值 这是正确的时候,否则同*.3
  "total_count":2,
  "total_fee":"0.200",
  "data":[
    {
      "mobile":"123****1234",
      "msg":"具体信息",
      "fee":0.05
    },
    {
      "mobile":"123****2234",
      "msg":"具体信息",
      "fee":0.15
    }
  ]
}

[
  [
    "extend",
    "时间",
    "mobile",
    "param",
    "fee",
    "errmsg",
    "reply"
  ],
  [
    //...
  ]
]

{ // 7 return message
  "fee":1.12,
  "paid":2.24
}

```

## 一些注意事项

- 传送中文时要指明使用`.encode()`
- 若传入是json但是不是字典呢？
- 注意数据库要正确设置时区
- 使用pyinstaller在win平台下编译的时候需要`from PyQt5 import sip`

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
  - 数据库重构
  - 后端对数据库IO进行封装
- 2018-07-01
  - 完善数据库IO的封装
  - 向云片网客服询问服务细节，发现可能无法满足需求
  - 转向腾讯云的SMS
  - 要根据新的细节重新设计数据库
  - 再次重构数据库，基本完成
  - 根据重构后的设计完成底层
- 2018-07-01~06
  - 完成除了接入腾讯以外的几乎全部工作,还除了打包发布和容器化
- 2018-09-22
  - 在网协面试中使用，出现了以下问题
  - 客户端的网络IO并非异步
  - 云片网修改了api,已做紧急修复
  - server中的一些print语句并没有出现在docker-compose的log上，很奇怪
  - 没有对重复手机号做区分
  - 接口的定义不够完善，已做修补