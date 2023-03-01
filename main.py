#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：main.py

@Author     : hsn

@Date       ：2023/3/1 下午8:35

@Version    : 1.0.0
"""
#  Copyright 2023. HCAT-Project-Team
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import datetime
import logging
import os.path
import subprocess
import sys

# check debug mode
debug = '--debug' in sys.argv

# set logger
logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                    format='[%(asctime)s][%(filename)s(%(lineno)d)][%(levelname)s] %(message)s',
                    datefmt='%b/%d/%Y-%H:%M:%S')

# create logs folder
if not os.path.exists('logs'):
    os.mkdir('logs')

# format the time
now = datetime.datetime.now()
formatted_time = now.strftime("%m-%d-%Y_%H:%M:%S")

# add file handler
handler = logging.FileHandler(
    os.path.join('logs', f'log_{formatted_time}_{int(now.now().timestamp() % 1 * 10 ** 6)}.txt'), encoding='utf8')
logging.getLogger().addHandler(handler)

# try to run thr `main` func
try:
    from _main import main
    main()
except ModuleNotFoundError as err:

    # install the requirements when `main` func throw 'ModuleNotFoundError'
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # retry
    from _main import main
    main()

except BaseException as err:

    # log the unknown error
    logging.critical('The function "main" could not be loaded, please check if the file is complete.')
    logging.exception(err)
    sys.exit()
