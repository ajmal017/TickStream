import sys
import os
import traceback
import json
sys.path.append(os.getcwd()[:os.getcwd().find("TickStream")+len("TickStream")])
from src.loghandler import log
from src.main.tick_stream_object import TickStreamObjects as tsobj
from src.broker.ib_service.ib_services import IBService
log = log.setup_custom_logger("tickstream")
SYM_MAP_PATH = tsobj.get_with_base_path("common", "ib_script_map", tsobj.get_value("common", "masters"))

class streamer(object):
    ibobj = IBService()
    def get_ib_symbol_from_map(self, nse_symbol):
        try:
            map_json = json.loads(open(str(SYM_MAP_PATH)).read())
            for sym in map_json:
                if sym['NSE_Symbol'] == nse_symbol:
                    return sym['IB_Symbol']
            return nse_symbol
        except Exception as ex:
            log.error("No mapping value found for NSE Symbol:%s" % nse_symbol)
            log.error(traceback.format_exc())

    def start_streaming(self):
        try:
            self.ibobj.connect_ib(self.ibobj)
            for contract in tsobj.ib_subcribed_scripts:
                self.ibobj.subscribe_contract(contract, self.ibobj)
                log.info("Sucessfully Subscribed "+ str(contract))
            self.ibobj.start_run(self.ibobj)
        except Exception as ex:
            log.error(ex)
            log.error(traceback.format_exc())

    def stop_streaming(self):
        try:
            for script in tsobj.ib_subcribed_scripts:
                self.ibobj.unsuscribe_contract(script,self.ibobj)
        except Exception as ex:
            log.error(ex)
            log.error(traceback.format_exc())

