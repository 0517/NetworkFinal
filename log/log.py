__author__ = 'qm'

# -*- coding: utf-8 -*-

import logging


class LoggingManagement:

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S', filename='server.log', filemode='a')
        self.logger = logging.getLogger()
        self.console = logging.StreamHandler()
        self.console.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        self.console.setFormatter(self.formatter)
        logging.getLogger('').addHandler(self.console)

    def DEBUG(self, message):
        logging.debug(message)

    def INFO(self, message):
        logging.info(message)

    # def ERROR(self, message):
    #     logging.error(message)

    def error(self, message):
        logging.error(message, exc_info=True)



