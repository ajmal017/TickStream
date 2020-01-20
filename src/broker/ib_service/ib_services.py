
import sys, os
import time
sys.path.append(os.getcwd()[:os.getcwd().find("TickStream")+len("TickStream")])
from src.loghandler import log
from src.main.tick_stream_object import TickStreamObjects as tsobj
log = log.setup_custom_logger("tickstream")
from src.broker.ib_service.ib_client_wrap import IBClient, IBWrapper
from ibapi.utils import iswrapper
from ibapi.contract import *
from ibapi.common import *
from ibapi.client import *
from ibapi.ticktype import *

from json import dumps
from kafka import KafkaProducer
from random import randint
import json
import traceback
import logging
import time

DEFAULT_GET_CONTRACT_ID = 43


producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'],
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))

TWS_IP = tsobj.get_value('ibconnect', 'gateway_ip')
TMS_PORT = int(tsobj.get_value('ibconnect', 'gateway_port'))
IB_CLIENT_ID = int(tsobj.get_value('ibconnect', 'IB_ClientId'))


class IBService(IBWrapper, IBClient):
    contract = None
    hdate_prev = tsobj.get_value('hrhd', 'back_test_prev_date')
    hdate = tsobj.get_value('hrhd', 'back_test_date')
    cdate = ""
    exe_iterator = 0
    back_test_symbol = tsobj.get_value('hrhd', 'back_test_symbol')
    running_hdate = False
    API_CONNECT = None
    def __init__(self):
        try:
            IBWrapper.__init__(self)
            IBClient.__init__(self, wrapper=self)
            self._my_contract_details = {}
        except Exception as ex:
            log.error(ex)
            log.error(traceback.format_exc())

    @staticmethod
    def connect_ib(ib_connection):
        try:
            if not ib_connection.isConnected():
                ib_connection.connect(TWS_IP, TMS_PORT, clientId=IB_CLIENT_ID)
                log.info("serverVersion:%s connectionTime:%s" % (ib_connection.serverVersion(),
                                                                    ib_connection.twsConnectionTime()))
        except Exception as ex:
            log.error(ex)
            log.error(traceback.format_exc())


    def get_stk_contract(self, symbol):
        try:
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.currency = "INR"
            contract.exchange = "NSE"
            return contract
        except Exception as ex:
            log.error(ex)
            log.error(traceback.format_exc())

    def get_time_stamp(self):
        ## Time stamp to apply to market data
        ## We could also use IB server time
        return int(time.time()) #datetime.datetime.now()

    @iswrapper
    # ! [tickprice]
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float,
                  attrib: TickAttrib):
        try:
            super().tickPrice(reqId, tickType, price, attrib)
            #print("TickPrice - TickerId:", reqId, "tickType:", tickType,
            #           "Price:", price, "localtime", str(self.get_time_stamp()))
            data = {"TickerId": reqId, "TopicId": str(tsobj.ib_subcribed_scripts[int(reqId)-1]['ibsymbol']), "Price": price, "Timestamp": str(self.get_time_stamp()) }
            producer.send(str(tsobj.ib_subcribed_scripts[int(reqId)-1]['ibsymbol']), value=data)
        except Exception as ex:
            log.error(ex)
            log.error(traceback.format_exc())


    @iswrapper
    def historicalTicksLast(self, reqId:int, ticks: ListOfHistoricalTickLast, done: bool):
        self.full_day_data(ticks)

    def subscribe_contract(self, symboldict, ibcon):
        try:
            self.contract = self.get_stk_contract(str(symboldict.get("ibsymbol")))
            ibcon.reqMktData(int(symboldict.get("reqid")), self.contract, "", False, False, [])
        except Exception as ex:
            log.error(ex)
            log.error(traceback.format_exc())

    def unsuscribe_contract(self, symboldict, ibcon):
        try:
            ibcon.cancelMktData(int(symboldict.get("reqid")))
        except Exception as ex:
            log.error(ex)
            log.error(traceback.format_exc())

    def start_run(self,ibcon):
        try:
            log.info("IB Service started running")
            ibcon.run()
        except Exception as ex:
            log.error(ex)
            log.error(traceback.format_exc())

    def full_day_data(self, ticks):
        try:

            if len(ticks) >= 1000:
                i = 0
                for tick in ticks:
                    str(time.strftime("%D %H:%M:%S", time.localtime(int(tick.time))))
                    data = {'Symbol': self.back_test_symbol, 'Price': tick.price, 'Timestamp': tick.time}
                    producer.send("HRHD", value=data)
                    i = i + 1
                    # if self.running_hdate is True:
                    #     print('Price - ', tick.price, 'Timestamp-', tick.time)
                    if i == 1000:
                        self.reqHistoricalTicks(randint(10, 999), self.contract,
                                                str(self.cdate) + " " +
                                                str(time.strftime("%H:%M:%S", time.localtime(int(tick.time)))),
                                                "", 1000, "TRADES", 1, True, [])
                        break
            else:
                for tick in ticks:
                    data = {'Symbol': self.back_test_symbol, 'Price': tick.price,
                            'Timestamp': tick.time}
                    # if self.running_hdate is True:
                    #     print('Price - ', tick.price, 'Timestamp-', tick.time)
                    producer.send("HRHD", value=data)
                if self.running_hdate is True:
                    time.sleep(100)
                    tsobj.slow_min_pd_DF.to_csv(r'~/Desktop/slow_' + self.back_test_symbol + '_' + self.hdate + '.csv')
                    tsobj.fast_min_pd_DF.to_csv(r'~/Desktop/fast_' + self.back_test_symbol + '_' + self.hdate + '.csv')
                    print("--------------------------------------------------------------------------------------")
                    print("-----Execution Completed For " + self.back_test_symbol + " & CSV Generated in Desktop-----")
                    print("--------------------------------------------------------------------------------------")
                    print("-------------------------Execution Completed For All the Symbols----------------------")
                    sys.exit()
                if self.running_hdate is False:
                    time.sleep(60)
                    print("Requesting current day data...")
                    self.running_hdate = True
                    tsobj.slow_min_ticks.clear()
                    tsobj.fast_min_ticks.clear()
                    # tsobj.c_fast_min = 18
                    self.cdate = self.hdate
                    tsobj.start_sapm = True
                    self.reqHistoricalTicks(1, self.contract, str(self.hdate) + " 09:15:00", "", 1000, "TRADES", 1,
                                             True, [])

        except Exception as ex:
            logging.error(traceback.format_exc())
            print(traceback.format_exc())

    def get_hrhd_data(self, ibcon):
        try:
            # self.back_test_symbol = self.back_test_symbols[self.exe_iterator]
            self.contract = self.get_stk_contract(self.back_test_symbol)
            self.cdate = self.hdate_prev
            ibcon.reqHistoricalTicks(1, self.contract, str(self.hdate_prev)+" 09:15:00", "", 1000, "TRADES", 1, True, [])
            ibcon.run()
        except:
            log.error(traceback.format_exc())
