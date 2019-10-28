import logging

import sys, os
sys.path.append(os.getcwd()[:os.getcwd().find("TickStream")+len("TickStream")])

import shutil
import traceback
from src.main.tick_stream_object import TickStreamObjects as streamObj


def setup_custom_logger(name):
    try:
        if not os.path.exists(streamObj.parser.get('common', 'log_path')):
            os.makedirs(streamObj.parser.get('common', 'log_path'))
        else:
            shutil.rmtree(streamObj.parser.get('common', 'log_path'))
            os.makedirs(streamObj.parser.get('common', 'log_path'))
        formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
        if streamObj.parser.get('common', 'log_level').lower() == "info":
            log_level = logging.INFO
        elif streamObj.parser.get('common', 'log_level').lower() == "debug":
            log_level = logging.DEBUG
        elif streamObj.parser.get('common', 'log_level').lower() == "error":
            log_level = logging.ERROR
        elif streamObj.parser.get('common', 'log_level').lower() == "warn":
            log_level = logging.WARN
        else:
            log_level = logging.INFO
        logfile = streamObj.parser.get('common', 'log_path')+os.sep+"tick_stream.log"
        handler = logging.FileHandler(logfile)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        logger.addHandler(handler)
        return logger
        # file_handler = logging.FileHandler(logfile)
        # stdout_handler = logging.StreamHandler(sys.stdout)
        # handlers = [file_handler, stdout_handler]
        # logging.basicConfig(
        #     level=log_level,
        #     format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        #     handlers=handlers
        # )
        # logger = logging.getLogger(name)
        # return logger
    except Exception as ex:
        logger.error(ex)
        logger.error(traceback.format_exc())
    return None