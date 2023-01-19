import logging
import os.path
import subprocess

if not os.path.exists('RPDB'):
    subprocess.check_call(['git', 'clone', 'https://github.com/hsn8086/RPDB.git'])
from server import Server

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(filename)s(%(lineno)d)][%(levelname)s] %(message)s',
                    datefmt='%b/%d/%Y-%H:%M:%S')

s = Server()
s.start()
