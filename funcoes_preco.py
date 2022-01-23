# Bibliotecas a serem importadas:
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
import talib
from scipy import stats
from mathmoments import mathmoments

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
    close_diff = abs(prices.diff())
    net_change = abs(prices.diff(timeperiod))
    
    # Calcular o efficiency ratio utilizando a fórmula
    # ERt = |P(t) - P(t-n)| /  Sum(i=t-n, i=t)(|P(i) - P(i-1)|)
    sum_change_diff = np.array([])
    sum_change = np.array([])
    er_mean = np.array([])
    for index in range(0, len(close_diff)):
    
        if index == 0:
            sum_change_diff = np.append(sum_change_diff, np.nan)
        else:
            sum_change_diff_aux = abs(close_diff[index])
            sum_change_diff = np.append(sum_change_diff, sum_change_diff_aux)
            
        if index < timeperiod:
            sum_change = np.append(sum_change, np.nan)
        else:
            sum_change = np.append(sum_change, 
                                np.sum(sum_change_diff[index-timeperiod+1:index+1]))
            
    efficiency_ratio = net_change / sum_change
    
    for index in range(0, len(close_diff)):
        if index < er_meanperiod:
            er_mean = np.append(er_mean, np.nan)
        else:
            er_mean = np.append(er_mean, 
                                np.mean(efficiency_ratio[index-er_meanperiod+1:index+1]))
    
    return efficiency_ratio, er_mean


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
                        
    return mean, std, skew, kurt

# Use to tests ->
# if __name__ == "__main__":
#     file='data/PETR4_Daily_202112010000_202201210000.csv'
#     symbol_data = organize_data(file)
#     efficiency_ratio, er_mean = get_efficiency_ratio(symbol_data['Close'], 20, 5)
#     mean, std, skew, kurt = get_stats(symbol_data['Close'], 20)
#     print(mean)
#     print(std)
#     print(skew)
#     print(kurt)