
import sys
import os
import json
sys.path.append(os.getcwd()[:os.getcwd().find("TickStream")+len("TickStream")])

from src.loghandler import log
from src.main.tick_stream_object import TickStreamObjects as tsobj
from src.main.streamer import streamer

log = log.setup_custom_logger("tickstream")


class Main(object):
    def __init__(self):
        try:
            log.info("TickStream service started")
            json_path = str(tsobj.basepath)+os.path.join(tsobj.get_value("common", "masters"),
                             tsobj.get_value("common", "stream_list"))
            log.info("Loading scripts details from json " + str(tsobj.get_value("common", "stream_list")))
            company_dicts = None
            if json_path:
                with open(json_path, 'r') as f:
                    company_dicts = json.load(f)
            log.info("List of company loaded \n"+ str(company_dicts))
            strmobj = streamer()
            log.info("Creating IB symbol mapping dictionary")
            for index, script in enumerate(company_dicts):
                tsobj.ib_subcribed_scripts.append({"reqid":index+1, "ibsymbol":strmobj.get_ib_symbol_from_map(script["Symbol"])})
            log.info("NSE and IB Symbol Mapping Done !! \n" + str(tsobj.ib_subcribed_scripts))
            if tsobj.ib_subcribed_scripts is not None:
                log.info("Tick Streamer starting streaming..")
                strmobj.start_streaming()
        except Exception as ex:
            log.error(ex)

if __name__ == "__main__":
    main = Main()
