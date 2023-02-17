<!-- TOC -->
* [前言](#前言)
* [服务器事件](#服务器事件)
  * [描述](#描述)
  * [基事件](#基事件)
    * [属性](#属性)
    * [方法](#方法)
  * [事件的创建](#事件的创建)
    * [存储位置](#存储位置)
    * [创建流程](#创建流程)
* [User类](#user类)
  * [描述](#描述-1)
  * [继承](#继承)
  * [属性](#属性-1)
  * [方法](#方法-1)
    * [__init__(self, user_id, password, user_name)](#init--self-userid-password-username-)
      * [参数](#参数)
    * [_var_init(self)](#-varinit--self-)
    * [change_password(self, password)](#changepassword--self-password-)
      * [参数](#参数-1)
    * [auth(self, password)](#auth--self-password-)
      * [参数](#参数-2)
      * [返回值](#返回值)
    * [add_user_event(self, ec: EventContainer)](#adduserevent--self-ec--eventcontainer-)
      * [参数](#参数-3)
    * [auth_token(self, token)](#authtoken--self-token-)
      * [参数](#参数-4)
      * [返回值](#返回值-1)
  * [使用示例](#使用示例)
* [群组类](#群组类)
  * [描述](#描述-2)
  * [继承](#继承-1)
  * [属性](#属性-2)
  * [方法](#方法-2)
    * [__init__(self, group_id)](#init--self-groupid-)
      * [参数](#参数-5)
    * [_var_init(self)](#-varinit--self--1)
    * [broadcast(self, server, user_id, ec)](#broadcast--self-server-userid-ec-)
      * [参数](#参数-6)
    * [permission_match(self, username, permission=Permission_ADMIN)](#permissionmatch--self-username-permissionpermissionadmin-)
      * [参数](#参数-7)
      * [返回值](#返回值-2)
  * [使用示例](#使用示例-1)
* [EventContainer类](#eventcontainer类)
  * [描述](#描述-3)
  * [属性](#属性-3)
  * [方法](#方法-3)
    * [__init__(self, data_base: RPDB)](#init--self-database--rpdb-)
      * [参数](#参数-8)
    * [__call__(self, key, value)](#call--self-key-value-)
      * [参数](#参数-9)
    * [write_in(self)](#writein--self-)
    * [add(self, key, value)](#add--self-key-value-)
      * [参数](#参数-10)
      * [返回值](#返回值-3)
  * [使用示例:](#使用示例-)
<!-- TOC -->

# 前言

在1.x版本的服务器中,我们已经意识到直接读写数据库会带来一些不可预见的问题,同时也发现了由于不完善的数据库模块所导致的逻辑混乱.因此,在假期期间,我们对服务器进行了重新编写,并优化了数据库模块,以期提供更好的开发体验.

这次重写的主要目的是为了优化开发流程,减少部分繁琐的重复操作,提高开发效率.但是,考虑到插件系统的开发并不是必要的,而且会增加日常开发的难度,我们决定将其删除.

# 服务器事件

## 描述

"服务器事件"(在本段中简称为 "事件")是服务器的基础,它是 API 的入口,也是某些方法的具体实现.

## 基事件

`BaseEvent`是所有事件的基类,作为`API`的入口和某些方法的具体实现.

### 属性

`BaseEvent`类有以下属性:

- `auth`: 表示事件是否需要认证,默认为启用验证.
- `req`: `Flask`框架默认使用的请求对象.
- `server`: 实例化的服务器类.
- `path`: 用户请求时的路径.
- `e_mgr`: 事件管理器,用于运行事件.
- `user_id`: 用户的id,必须要登录后才能获取.

### 方法

`BaseEvent`类有以下方法:

- `run()`: 运行事件,检查请求参数的完整性,并运行`_run`函数处理逻辑.
- `_run()`: 具体的事件处理逻辑实现.

## 事件的创建

### 存储位置

所有的事件类必须在`event`目录下创建.

### 创建流程

1. 创建事件文件,请使用`下划线命名法`(`underscore_case`).
2. 在刚才创建的文件中创建类,类名应与刚刚文件名相同,请使用`大写驼峰命名法`(`PascalCase`).
3. 设置验证模式,默认为启用验证.
4. 定义入口函数.

代码示例:

```python
from event.base_event import BaseEvent


class MyEvent(BaseEvent):
    auth = False

    def _run(self, arg1, arg2='default value'):
        # 处理逻辑
        ...
```

在创建`MyEvent`时,`auth`设置为`False`,表示该事件不需要认证.

`_run`函数是事件的入口函数,接受请求传递的参数,处理逻辑,并返回结果.

# User类

## 描述

User类代表一个聊天应用中的用户,包含了用户的一些基本信息,权限验证和事件管理.

## 继承

User类继承自Jelly类.

## 属性

- todo_list: 待办事项列表,类型为列表
- token: 用户令牌,类型为字符串
- status: 用户状态,类型为字符串
- friend_dict: 用户的好友字典,类型为字典
- groups_dict: 用户的群组字典,类型为字典
- e_mail_auth: 是否已完成邮箱认证,类型为布尔值

## 方法

### __init__(self, user_id, password, user_name)

构造函数,用于初始化User类的实例,包括传入的参数.

#### 参数

- user_id: str类型,用户ID
- password: str类型,用户密码
- user_name: str类型,用户名

### _var_init(self)

初始化User实例的变量.

### change_password(self, password)

修改用户密码,并生成密码哈希值和salt.

#### 参数

- password: str类型,新密码

### auth(self, password)

验证用户密码是否正确.

#### 参数

- password: str类型,待验证的密码

#### 返回值

- 如果密码验证通过,返回True;否则返回False.

### add_user_event(self, ec: EventContainer)

添加用户事件到待办事项列表.

#### 参数

- ec: EventContainer类型,待添加的事件容器.

### auth_token(self, token)

验证用户令牌是否正确.

#### 参数

- token: str类型,待验证的用户令牌

#### 返回值

- 如果令牌验证通过,返回True;否则返回False.

## 使用示例

假设我们在一个聊天应用中需要创建一个新用户,我们可以使用User类来创建一个新用户对象,然后对用户进行各种操作,比如修改密码,添加待办事项,添加好友,加入群组等。

首先,我们需要实例化User类并传入用户ID,密码和用户名:

```
user = User('jane123', 'password123', 'Jane')
```

接着,我们可以使用add_user_event()方法向用户待办事项列表中添加事件容器:

```
ec = EventContainer(db_event)
ec.add('type', 'message')
ec.add('friend_id', '789012')
ec.add('msg', 'Hello, how are you?')
ec.add('time', time.time())
user.add_user_event(ec)
```

然后,我们可以使用change_password()方法修改用户密码:

```
user.change_password('newpassword123')
```

接着,我们可以使用auth()方法验证用户密码是否正确:

```
if user.auth('newpassword123'):
    print('Password is correct')
else:
    print('Password is incorrect')
```

然后,我们可以使用auth_token()方法验证用户令牌是否正确:

```
if user.auth_token('mytoken'):
    print('Token is correct')
else:
    print('Token is incorrect')
```

这样,我们就成功地创建了一个新用户,并对其进行了各种操作,比如添加待办事项,修改密码,验证密码和令牌,添加好友等。

# 群组类

## 描述

Group类代表一个聊天应用中的群组,包含了群组的一些基本信息,成员管理和事件广播.

## 继承

Group类继承自Jelly类.

## 属性

- id: 群组ID,类型为字符串
- name: 群组名称,类型为字符串
- member_dict: 群组成员字典,类型为字典,key为用户ID,value为用户对象
- owner: 群主用户名,类型为字符串
- admin_list: 管理员用户名集合,类型为集合
- member_settings: 成员设置字典,类型为字典,key为用户ID,value为成员设置对象
- ban_dict: 封禁成员字典,类型为字典,key为用户ID,value为封禁对象
- group_settings: 群组设置字典,类型为字典,包含验证方式,问题,答案等设置

## 方法

### __init__(self, group_id)

构造函数,用于初始化Group类的实例,包括传入的参数.

#### 参数

- group_id: str类型,群组ID

### _var_init(self)

初始化Group实例的变量.

### broadcast(self, server, user_id, ec)

向群组成员广播事件.

#### 参数

- server: Server类型,服务器对象
- user_id: str类型,广播事件的用户ID
- ec: EventContainer类型,待广播的事件容器

### permission_match(self, username, permission=Permission_ADMIN)

验证用户权限是否符合要求.

#### 参数

- username: str类型,待验证的用户名
- permission: int类型,期望的权限等级

#### 返回值

- 如果用户权限符合要求,返回True;否则返回False.

## 使用示例

假设我们在一个聊天应用中想要创建一个新的群组,并向其中添加成员,我们可以使用Group类来实现。

首先,我们需要实例化Group类并传入群组ID:

```
group = Group('group_123')
```

接着,我们可以向群组中添加成员,如下所示:

```
group.add_member(user1)
group.add_member(user2)
group.add_member(user3)

```

然后,我们可以将群主设置为其中的某个成员,如下所示:

```
group.owner=user1.user_id
```

接着,我们可以将某个成员设置为管理员,如下所示:

```
group.admin_list.add(user2.user_id)
```

最后,我们可以向群组中广播一条消息,如下所示:

```
ec = EventContainer(db_event)
ec.add('type', 'message')
ec.add('sender', 'user_1')
ec.add('msg', 'Hello, group!')
ec.add('time', time.time())
group.broadcast(server, user1.username, ec)
```

这样,我们就成功地创建了一个新的群组,并向其中添加了成员,设置了群主和管理员,并且向群组中广播了一条消息。

# EventContainer类

## 描述

EventContainer类是一个事件容器类,用于存储**聊天应用中的各种事件信息**.注:与服务器事件无关.

## 属性

- data_base: RP-DataBase数据库对象,用于存储事件信息.
- rid: str类型,表示事件的唯一标识符.
- json: dict类型,存储事件的json数据.
- can_write: bool类型,表示是否允许写入数据.

## 方法

### __init__(self, data_base: RPDB)

构造函数,用于初始化EventContainer类的实例,包括传入的参数.

#### 参数

- data_base: RPDB类型,RP-DataBase数据库对象.

### __call__(self, key, value)

用于设置事件的键值对.

#### 参数

- key: str类型,表示事件的键.
- value: str类型,表示事件的值.

### write_in(self)

将事件写入RP-DataBase数据库.

### add(self, key, value)

添加事件的键值对.

#### 参数

- key: str类型,表示事件的键.
- value: str类型,表示事件的值.

#### 返回值

- 返回添加完键值对后的EventContainer实例.

## 使用示例:

假设我们在一个聊天应用中想要记录用户发送的消息,我们可以使用EventContainer类来记录用户消息事件,然后将事件添加到用户的待办事项列表中。

首先,我们需要实例化EventContainer类并传入RPDB类型的数据库:

```
ec = EventContainer(db_event)
```

接着,我们可以使用add()方法向事件容器添加各种属性:

```
ec.add('type', 'message')
ec.add('friend_id', 'f789012')
ec.add('msg', 'Hello, how are you?')
ec.add('time', time.time())
```

其中,'f789012'是一个例子,表示以字母"f"开头的用户ID。

然后,我们可以使用write_in()方法将事件容器中的属性写入数据库中:

```
ec.write_in()
```

最后,我们可以将事件添加到用户的待办事项列表中:

```
user.add_user_event(ec)
```

这样,我们就成功地记录了用户发送的消息,并将其添加到了用户的待办事项列表中。