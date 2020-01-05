import sys, os
import json
sys.path.append(os.getcwd()[:os.getcwd().find("TickStream")+len("TickStream")])
from src.main.tick_stream_object import TickStreamObjects as tsobj


class GetPipeList(object):

    def __init__(self):

        try:

            json_path = str(tsobj.basepath)+os.path.join(tsobj.get_value("common", "masters"),
                             tsobj.get_value("common", "stream_list"))
            company_list = None
            pipelist = ""
            if json_path:
                with open(json_path, 'r') as f:
                    company_dicts = json.load(f)
            for index, script in enumerate(company_dicts):
                pipelist = self.get_ib_symbol_from_map(script["Symbol"]) + ","  + pipelist
            print(pipelist)
        except Exception as ex:
            print(ex)

    def get_ib_symbol_from_map(self, nse_symbol):
        try:
            SYM_MAP_PATH = tsobj.get_with_base_path("common", "ib_script_map", tsobj.get_value("common", "masters"))
            map_json = json.loads(open(str(SYM_MAP_PATH)).read())
            for sym in map_json:
                if sym['NSE_Symbol'] == nse_symbol:
                    return sym['IB_Symbol']
            return nse_symbol
        except Exception as ex:
            print("No mapping value found for NSE Symbol:%s" % nse_symbol)
            print(traceback.format_exc())

            
if __name__ == "__main__":
    main = GetPipeList()

