import pandas as pd
import numpy as np
from parsing import add_current_price

# datos
data_arg = pd.read_pickle("data/data_ARG.pkl")
data_us = pd.read_pickle("data/data_US.pkl")
target_by_sector = pd.read_pickle("data/target_by_sector.pkl")

# interseccion entre cedears e indice
data = pd.merge(data_us, data_arg, left_index=True, right_index=True)

# activos faltantes en la interseccion
faltantes = data_us[~data_us.index.isin(data.index)]
# Todo ok! los faltantes no tienen cedear.

# testeando precios.
test = add_current_price(data)
