import talib as tb
import numpy as np

inputs = {
    'open': np.random.random(1),
    'high': np.random.random(1),
    'low': np.random.random(1),
    'close': np.random.random(1)
}

print(inputs)

avgPrice=tb.AVGPRICE(inputs['open'],inputs['high'],inputs['low'],inputs['close'])
medPrice=tb.MEDPRICE(inputs['high'],inputs['low'])
typePrice=tb.TYPPRICE(inputs['high'],inputs['low'],inputs['close'])
wclPrice=tb.WCLPRICE(inputs['high'],inputs['low'],inputs['close'])
print(wclPrice)
print(typePrice)
print(medPrice)
print(avgPrice)