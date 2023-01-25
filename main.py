import logging
import os.path
import subprocess

'''if not os.path.exists(os.path.join(os.getcwd(), 'RPDB')):
    subprocess.check_call(['git', 'clone', 'https://github.com/hsn8086/RPDB.git'])'''
from server import Server

debug = True
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(filename)s(%(lineno)d)][%(levelname)s] %(message)s',
                    datefmt='%b/%d/%Y-%H:%M:%S')

s = Server(debug=debug)
s.start()
