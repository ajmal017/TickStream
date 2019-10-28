

PROJECT_NAME = "TickStream"
LOG_NAME = "tickstream"

from configparser import ConfigParser
import os,sys
sys.path.append(os.getcwd()[:os.getcwd().find(PROJECT_NAME)+len(PROJECT_NAME)])



class TickStreamObjects(object):

    parser = ConfigParser()
    basepath = os.getcwd()[:os.getcwd().find(PROJECT_NAME)+len(PROJECT_NAME)]
    parser.read(os.path.join(basepath,"config","config.ini"))

    ib_subcribed_scripts = []

    @staticmethod
    def get_with_base_path(head, key, folder=""):
        return os.getcwd()[:os.getcwd().find(PROJECT_NAME)+len(PROJECT_NAME)] + os.path.join(folder + TickStreamObjects.parser.get(head, key))

    @staticmethod
    def get_value(head, key):
        return TickStreamObjects.parser.get(head, key)