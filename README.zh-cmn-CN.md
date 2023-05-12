# 目录

<!-- TOC -->
* [目录](#目录)
* [介绍](#介绍)
* [安装](#安装)
  * [服务端](#服务端)
  * [客户端](#客户端)
* [运行](#运行)
* [已实现的功能](#已实现的功能)
* [待办列表](#待办列表)
* [项目结构](#项目结构)
* [开发指南](#开发指南)
* [维护者](#维护者)
* [许可证](#许可证)
* [免责声明](#免责声明)
<!-- TOC -->

# 介绍

re_hcat-server是[HCat](https://hcat.online)的重置版服务器,基于Python开发.本项目使用AGPLv3许可证.

我们欢迎更多开发者加入我们的项目,一起构建更加完善的HCat服务器!

# 安装

## 服务端

目前,服务端暂未提供发行版(未来大概也不会提供),请使用Git获取服务端:

```shell
git clone https://github.com/HCAT-Project/re_hcat-server.git
pip install -r requirements.txt
```

## 客户端

如果您下载并正确配置了git,那当服务端启动时,会自动从github仓库克隆客户端.
并在[http://127.0.0.1:8080/](http://127.0.0.1:8080/index.html)开放.

当然您可以修改配置文件中的`/client/client-branch`以关闭或更改客户端版本.

下表是客户端的版本号和对应的分支:

| 分支       | 值      | 注释       |
|----------|--------|----------|
| 主分支(稳定版) | "main" | 稳定?大概... |
| 开发版      | "dev"  |          |
| 不启用客户端   | null   |          |

# 运行

```shell
python start.py
```

# 已实现的功能

- 账户管理:注册,登录,修改密码,更改用户昵称,获取用户信息,邮箱绑定等
- 好友管理:添加好友,删除好友,设置好友昵称,获取好友列表,获取好友信息等
- 群组管理:创建群组,加入群组,离开群组,更改群组名称,更改群组设置,转移群主,获取群组列表等
- 聊天功能:私聊,群聊,发送文字,图片,文件上传等

# 待办列表

- 完善权限管理系统
- 增加用户个性化设置
- 服务器主从机
- 多设备协同
- 后台管理
- 删除群组/注销账号
- 增加多种加好友方式

# 项目结构

点此查看:[项目结构](doc/project_structure_zh-hans.md)

**不保证实时更新**

# 开发指南

点此查看:[开发指南](doc/dev_guide_zh-hans.md)

# 维护者

[@hsn8086](https://github.com/hsn8086)

# 许可证

```
本程序为自由软件，在自由软件联盟发布的GNU通用公共许可协议的约束下，你可以对其进行再发布及修改。协议版本为第三版或（随你）更新的版本。
我们希望发布的这款程序有用，但不保证，甚至不保证它有经济价值和适合特定用途。详情参见GNU通用公共许可协议。
你理当已收到一份GNU通用公共许可协议的副本，如果没有，请查阅<http://www.gnu.org/licenses/>
```

# 免责声明

本项目仅供学习交流使用,使用者应遵守所在国家和地区的相关法律法规,对于任何非法使用所产生的后果,本项目概不负责.
