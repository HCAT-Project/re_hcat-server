English | [中文(普通话-大陆)](README.zh-cmn-CN.md)

# Table of Contents

<!-- TOC -->

* [Table of Contents](#table-of-contents)
* [Introduction](#introduction)
* [Installation](#installation)
    * [Server](#server)
    * [Client](#client)
* [Running](#running)
* [Features Implemented](#features-implemented)
* [To-Do List](#to-do-list)
* [Document](#document)
* [Maintainers](#maintainers)
* [License](#license)
* [Disclaimer](#disclaimer)

<!-- TOC -->

# Introduction

re_hcat-server is a reset version server of [HCat](https://hcat.online), developed with Python. This project is licensed
under the AGPLv3 license.

We welcome more developers to join our project and build a more perfect HCat server together!

# Installation

## Server

Currently, the server is not available in any release version(It may not be available in the future). Please use Git to
get the server:

```shell
git clone https://github.com/HCAT-Project/re_hcat-server.git
pip install -r requirements.txt
```

## Client

If you have downloaded and configured git correctly, the client will be automatically cloned from the GitHub repository
when the server starts. And it will be available at [http://localhost:8080/](http://localhost:8080/).

Laptops for unknown reasons you may need to manually execute the following command.

```shell
cd static
npm install
npm run build
```

Of course, you can disable or change the client version by modifying the `/client/client-branch` setting in the
configuration file.

The following table shows the version number and corresponding branch of the client:

| Branch         | Value  | Comment          |
|----------------|--------|------------------|
| Main (stable)  | "main" | Stable? Maybe... |
| Development    | "dev"  |                  |
| Disable client | "null" |                  |

# Running

**Please run with `Python 3.11` and above!**

```shell
python start.py
```

In addition, I strongly recommend using a server such as nginx to reverse proxy api and distribute static resources!

Also, use port 443(https,wss) or 80(http,ws) for external open ports if possible.

# Features Implemented

- Account Management: Register, login, change password, change user nickname, get user information, email binding, etc.
- Friend Management: Add friends, delete friends, set friend nicknames, get friend lists, get friend information, etc.
- Group Management: Create groups, join groups, leave groups, change group names, change group settings, transfer group
  ownership, get group lists, etc.
- Chatting Function: Private chat, group chat, sending text, images, upload file etc.

# To-Do List

- Add user personalization settings.
- Server master-slave.
- Multi-device collaboration.
- Backend management.
- Delete groups/cancel accounts.
- Add multiple ways to add friends.

# Document

| Document                                                    | Remarks      |
|-------------------------------------------------------------|--------------|
| [Project Structure](doc/project-structure_en-US.md)         |              |
| [Development Guide](doc/dev-guide_en-US.md)                 |              |
| [Translation Guide](doc/how-to-translate-the-hcat_en-US.md) | English only |

# Maintainers

[@hsn8086](https://github.com/hsn8086)

# License

```
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
We hope this program will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
```

# Disclaimer

This project is for learning and communication only. Users should comply with the relevant laws and regulations of their
country or region. This project is not responsible for any consequences of illegal use.
