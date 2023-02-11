def main():
    import logging
    import sys

    '''if not os.path.exists(os.path.join(os.getcwd(), 'RPDB')):
        subprocess.check_call(['git', 'clone', 'https://github.com/hsn8086/RPDB.git'])'''
    from server import Server

    debug = '--debug' in sys.argv

    handler = logging.FileHandler('log.txt', encoding='utf8')
    logging.getLogger().addHandler(handler)
    s = Server(debug=debug)
    s.start()
