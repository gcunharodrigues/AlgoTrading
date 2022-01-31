# Importando bibliotecas

import json
from time import sleep
from threading import Thread
from os.path import join, exists
from traceback import print_exc
from random import random
from datetime import datetime, timedelta

from api.dwx_client import dwx_client

# Função para obter os dados históricos.

def send_historic_data(MT4_files_dir, symbol, timeframe, start, end):
    dwx = dwx_client(metatrader_dir_path=MT4_files_dir)
    sleep(1)
    dwx.get_historic_data(symbol, timeframe, start, end)
    sleep(10)
    for st in dwx.historic_data.keys():
        on_historic_data(symbol, timeframe, dwx.historic_data[st])
        historic_data_list = []
        for k, v in dwx.historic_data[st].items():
            historic_time_list = []
            historic_time_list.append(k)
            for data in v:
                historic_time_list.append(dwx.historic_data[st][k][data])
            
            historic_data_list.append(historic_time_list)

    return historic_data_list
                
# Function to print historic data information.
def on_historic_data(symbol, time_frame, data):
        
    # you can also access the historic data via self.dwx.historic_data. 
    print('historic_data:', symbol, time_frame, f'{len(data)} bars')


# MT4_files_dir = 'C:/Users/guicr/AppData/Roaming/MetaQuotes/Terminal/'\
#                 'D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/'
# MT4_files_dir = '/home/gcunharodrigues/.wine/drive_c/Program Files/MetaTrader 5/MQL5/Files/'
# symbol = 'WIN$'
# timeframe = 'H4'
# start = datetime(2020, 1, 1).timestamp()
# end = datetime(2020, 1, 3).timestamp()

# historic_data = send_historic_data(MT4_files_dir, symbol, timeframe, start, end)
# print(historic_data)