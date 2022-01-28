from math import sqrt
import math

def mathmoments(array, start, count):
    mean = 0
    variance = 0
    skewness = 0
    kurtosis = 0
    
    size = len(array)
    data_count = 0
    
    if data_count == len(array):
        data_count = size
    else:
        data_count = count
    
    if data_count == 0:
        return math.nan
    if data_count + start > size:
        return math.nan
    
    ind1 = start
    ind2 = ind1 + data_count - 1
    
    for i in range(ind1, ind2+1):
        mean += array[i]
    mean = mean / data_count
    
    S = 0.0
    
    if data_count > 1:
        for i in range(ind1, ind2+1):
            variance += (array[i] - mean)**2
        variance = variance / (data_count)
        S = sqrt(variance)
    else:
        variance = math.nan
    
    if data_count > 2 and S > 0:
        for i in range(ind1, ind2+1):
            skewness += (array[i] - mean)**3
        skewness = skewness / (data_count)
        skewness = skewness / (S**3)
    else:
        skewness = math.nan
        
    if data_count > 3 and S > 0:
        for i in range(ind1, ind2+1):
            kurtosis += (array[i] - mean)**4
        kurtosis = kurtosis / (data_count)
        kurtosis = kurtosis / (S**4)
        kurtosis = kurtosis - 3
    else:
        kurtosis = math.nan
        
    return mean, variance, skewness, kurtosis