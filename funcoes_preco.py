# Bibliotecas a serem importadas:
import pandas as pd
import numpy as np
import talib
from scipy import stats
from mathmoments import mathmoments
import math
import statistics
from datetime import datetime, timedelta

def organize_data(file):
    # Leitura do arquivo CSV extraído do MT5
    symbol_data = pd.read_csv(file, sep='\t')

    # Integrando as colunas <DATE> e <TIME> em uma única coluna Date,e 
    # renomeando as colunas.
    if '<TIME>' in symbol_data:
        symbol_data['Date'] = symbol_data['<DATE>'] + ' ' + symbol_data['<TIME>']
        col = symbol_data.pop('Date')
        symbol_data.insert(0, "Date", col)
        symbol_data.drop(['<DATE>','<TIME>'], axis=1, inplace=True)
    else:
        symbol_data = symbol_data.rename(columns={'<DATE>':'Date'})

    symbol_data = symbol_data.rename(columns={
        '<CLOSE>': 'Close', 
        '<HIGH>': 'High', 
        '<LOW>': 'Low', 
        '<OPEN>': 'Open', 
        '<VOL>': 'Volume',
        '<TICKVOL>': 'TickVolume',
        '<VOLUME>': 'RealVolume',
        '<SPREAD>': 'Spread',
        })
    
    # No caso de arquivos advindos do MT5, trocar apenas o tipo da coluna 
    # 'Date'.
    symbol_data['Date'] = pd.to_datetime(symbol_data['Date'])
    
    # Verificar a sequência de valores no Date Time, se estão em ordem 
    # crescente ou descrescente em relação ao tempo. Caso estiver em ordem 
    # crescente, continuar da mesma forma, caso contrário, inverter a ordem.
    
    # Diferença entre os elementos:
    delta = symbol_data['Date'].diff()
    
    # Validação da ordem dos elementos:
    if delta[1] > pd.Timedelta(0):
        ordem = 'crescente'
    else:
        ordem = 'decrescente'
        
    # Caso esteja em ordem decrescente, inverter a ordem:
    if ordem == 'descrescente':
        symbol_data = symbol_data.sort_values(by='Date', ascending=False)
        
    return symbol_data

def get_efficiency_ratio(prices, timeperiod=10, er_meanperiod=10):
    """Função para calcular o efficiency ratio conforme Perry Kaufmann.
    Visa medir se os preços em período de tempo apresentam tendência ou 
    não. Varia de 0 a 1 (0 = não tendência, 1 = tendência).
    price = array de preços
    timeperiod = período de tempo - padrão 10
    retorna array efficieny ratio"""
    # Calcular a diferença entre os preços:
    close_diff = abs(prices.diff()).tolist()
    net_change = abs(prices.diff(timeperiod)).tolist()

    # Calcular o efficiency ratio utilizando a fórmula
    # ERt = |P(t) - P(t-n)| /  Sum(i=t-n, i=t)(|P(i) - P(i-1)|)
    sum_change_diff = []
    sum_change = []
    er_mean = []
    for index in range(0, len(close_diff)):
    
        if index == 0:
            sum_change_diff.append(math.nan)
        else:
            sum_change_diff_aux = abs(close_diff[index])
            sum_change_diff.append(sum_change_diff_aux)
            
        if index < timeperiod:
            sum_change.append(math.nan)
        else:
            sum_change.append(sum(sum_change_diff[index-timeperiod+1:index+1]))
            
    efficiency_ratio = np.divide(net_change,sum_change).tolist()
    
    for index in range(0, len(close_diff)):
        if index < er_meanperiod:
            er_mean.append(math.nan)
        else:
            er_mean.append(statistics.mean(efficiency_ratio[index-er_meanperiod+1:index+1]))
    
    efficiency_ratio_data = {'efficiency_ratio': efficiency_ratio, 
                             'er_mean': er_mean}
    
    return efficiency_ratio_data


def get_stats(prices, timeperiod=10):
    """Função para calcular as estatísticas - Média, Desvio Padrão, Skew e
    Kurtosis.
    price = array de preços
    timeperiod = período de tempo - padrão 10
    retorna arrays da média, desvio padrão, skew e kurtosis"""
    
    mean = np.array([])
    variance = np.array([])
    skew = np.array([])
    kurt = np.array([])
    for index in range(0, len(prices)):
        if index < timeperiod:
            mean = np.append(mean, np.nan)
            variance = np.append(variance, np.nan)
            skew = np.append(skew, np.nan)
            kurt = np.append(kurt, np.nan)
        else:
            mean_aux, variance_aux, skew_aux, kurt_aux = mathmoments(prices,
                                                            index-timeperiod+1,
                                                            timeperiod)
            mean = np.append(mean, mean_aux)
            variance = np.append(variance, variance_aux)
            skew = np.append(skew, skew_aux)
            kurt = np.append(kurt, kurt_aux)
            
    std = np.sqrt(variance)
    
    stats = {'mean': mean, 'std': std, 'skewness': skew, 'kurtosis': kurt}
                        
    return stats

def zigzag(prices, period=12, deviation=5, backstep=3, spread=0.01):
    """"Enviar o dataframe eqty_table para a variável prices.
    Os cálculos necessitarão de High and Low."""
    low = prices['Low']
    high = prices['High']
    
    zigzagbuffer = []
    lowmapbuffer = []
    highmapbuffer = []
    
    last_low = 0
    last_high = 0
    
    extreme_search = 'extremum'
    
    # Searching for high and low extremes
    for row in prices.index:
        if row < period:
            zigzagbuffer.append(0)
            lowmapbuffer.append(0)
            highmapbuffer.append(0)
            continue
        
        zigzagbuffer.append(0)
        lowmapbuffer.append(0)
        highmapbuffer.append(0)
        
        # Low extremes
        val = low.iloc[row+1-period:row+1].min()
        if val == last_low:
            val = 0
        else:
            last_low = val
            if (low[row] - val) > deviation * spread:
                val = 0
            else:
                for back in range(1, backstep+1):
                    res = lowmapbuffer[row-back]
                    if res != 0 and res > val:
                        lowmapbuffer[row-back] = 0
        if low[row] == val:
            lowmapbuffer[row] = val
        else:
            lowmapbuffer[row] = 0
                                
        # High extremes
        val = high.iloc[row+1-period:row+1].max()
        if val == last_high:
            val = 0
        else:
            if (val - high[row]) > deviation * spread:
                val = 0
            else:
                for back in range(1, backstep+1):
                    res = highmapbuffer[row-back]
                    if res != 0 and res < val:
                        highmapbuffer[row-back] = 0
        if high[row] == val:
            highmapbuffer[row] = val
        else:
            highmapbuffer[row] = 0
            

    last_low = 0
    last_high = 0
    
    #ZigZag
    for row in prices.index: 
        #Extreme search
        if extreme_search == 'extremum':
            if highmapbuffer[row] != 0:
                last_high = high[row]
                last_high_pos = row
                extreme_search = 'bottom'
                zigzagbuffer[row] = last_high
            if lowmapbuffer[row] != 0:
                last_low = low[row]
                last_low_pos = row
                extreme_search = 'peak'
                zigzagbuffer[row] = last_low
            continue
        
        elif extreme_search == 'peak':
            if lowmapbuffer[row] != 0 and lowmapbuffer[row] < last_low and \
                highmapbuffer[row] == 0:
                zigzagbuffer[last_low_pos] = 0
                last_low_pos = row
                last_low = lowmapbuffer[row]
                zigzagbuffer[row] = last_low
            if highmapbuffer[row] != 0 and lowmapbuffer[row] == 0:
                last_high = highmapbuffer[row]
                last_high_pos = row
                zigzagbuffer[row] = last_high
                extreme_search = 'bottom'
            continue
        
        elif extreme_search == 'bottom':
            if highmapbuffer[row] != 0 and highmapbuffer[row] > last_high and \
                lowmapbuffer[row] == 0:
                zigzagbuffer[last_high_pos] = 0
                last_high_pos = row
                last_high = highmapbuffer[row]
                zigzagbuffer[row] = last_high
            if lowmapbuffer[row] != 0 and highmapbuffer[row] == 0:
                last_low = lowmapbuffer[row]
                last_low_pos = row
                zigzagbuffer[row] = last_low
                extreme_search = 'peak' 
            continue        

    buffers = {'zigzag': zigzagbuffer, 'lows': lowmapbuffer, 
               'highs': highmapbuffer}
    
    return buffers

# Use to tests ->
if __name__ == "__main__":
    file='data/PETR4_M5.csv'
    symbol_data = organize_data(file)
    start = datetime(2021, 12, 22)
    end = datetime(2021, 12, 31)
    eqty_table = symbol_data.loc[(symbol_data['Date'] >= start) 
            & (symbol_data['Date'] <= end)].copy()
    eqty_table.reset_index(inplace=True, drop=True)
    zigzag_data = zigzag(eqty_table)
    print(zigzag_data['zigzag'])