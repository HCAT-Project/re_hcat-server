#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : start.py

@Author     : hsn

@Date       : 2023/3/1 下午8:35

@Version    : 1.0.0
"""

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
import datetime
import logging
import os.path
import subprocess
import sys
if __name__ == '__main__':
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
        os.path.join('logs', f'log_{formatted_time}_{int(now.now().timestamp() % 1 * 10 ** 6)}.txt').replace(':', '_'),
        encoding='utf8')
    logging.getLogger().addHandler(handler)

    # try to run thr `main` func

    try:
        from src.main import main
        from src.util.i18n import gettext_func as _
        main()
    except ModuleNotFoundError as err:

        # install the requirements when `main` func throw 'ModuleNotFoundError'
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

        from src.main import main

        main()
    except ImportError:

        # update the requirements when `main` func throw 'ImportError'
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--upgrade'])

        # retry
        from src.main import main

        main()
    except BaseException as err:

        # log the unknown error
        logging.critical(_('The function "main" could not be loaded, please check if the file is complete.'))
        logging.exception(err)
        sys.exit()
