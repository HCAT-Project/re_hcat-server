#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Copyright (C) 2023. HCAT-Project-Team
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
@File       : gen_msg_po.py

@Author     : hsn

@Date       : 3/17/23 5:19 PM

@Version    : 1.0.0
"""
import os
import subprocess

lang = input("language(such as zh_CN or en_US): ")
os.makedirs(os.path.join('locale', lang, 'LC_MESSAGES'), exist_ok=True)
subprocess.check_call(['msginit', '--locale', f'locale/{lang}/LC_MESSAGES/all.po', '-i', 'messages.pot'])
