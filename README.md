# 项目进度

<!-- 主板本.功能.bug -->
## 1.0.0 版本计划

- [x] 数据库设计
- [x] 数据库IO底层实现,并且写好注释
- [x] 完成基础的GUI
- [x] 重写数据库，底层也不再对单条发送作区分，仅提供查询的接口
- [x] 后端与客户端的通信接口统一出来，要和数据库匹配，而独立于api调用
- [x] GUI完善异常处理
- [x] GUI重构提示信息的输出模式
- [x] GUI增加发送结果的页面
- [x] 增加模板管理的功能
- [x] 支持导入CVS
- [x] 支持对行列的直接增减
- [x] 支持导出表格
- [x] 针对utf-8做优化
- [x] 可以刷新状态
- [x] 利用get方法传送可选信息
- [x] 规定从服务端到客户端返回的数据接口格式
- [x] 重新整理接口，保留腾讯的代码
- [x] 重构数据库模板的库，要区分不同api的模板
- [x] 查询历史发送消息的功能
- 7/7
  - [x] 未联网情况下无法流畅加载的情况 timeout 

##
- 管理工具
  - [ ] 支持增加用户
  - [ ] 查看当前用户信息
  - [ ] 建立数据库
- 客户端
  - [ ] 增强用户体验（增加提示，用户说明）
  - [ ] 完善密码的逻辑，支持修改密码
  - [ ] 完善使用文档
  - [ ] 完善注释
  - [x] 使用配置文件
  - [ ] 发布客户端
- 服务端
  - [ ] 整理内部输出信息,并采用logging模块
  - [ ] 对腾讯云的api进行研究
  - [ ] 完善注释
  - [ ] 完善使用文档
  - [x] 服务端容器化 `2018-07-10`
  - [x] 服务端与数据库使用docker-compose构建 `2018-07-11`
  - [x] 使用配置文件 `2018-07-10`
- 其他
- [ ] 代码优化/封装
- [ ] 列出git-repo目录解构