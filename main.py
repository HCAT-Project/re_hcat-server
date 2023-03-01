#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：main.py

@Author     : hsn

@Date       ：2023/3/1 下午6:29

@Version    : 1.0.0
"""
#  Copyright 2023. hsn
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

import logging
import subprocess
import sys

debug = '--debug' in sys.argv
logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                    format='[%(asctime)s][%(filename)s(%(lineno)d)][%(levelname)s] %(message)s',
                    datefmt='%b/%d/%Y-%H:%M:%S')

handler = logging.FileHandler('log.txt', encoding='utf8')
logging.getLogger().addHandler(handler)

try:
    from _main import main
except Exception as err:
    logging.critical('The function "main" could not be loaded, please check if the file is complete.')
    logging.exception(err)
    sys.exit()

try:
    main()
except ModuleNotFoundError as err:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    main()
except BaseException as err:
    logging.exception(err)
