import pandas as pd
import numpy as np
from parsing import add_current_price

# datos
data_arg = pd.read_pickle("data/data_ARG.pkl")
data_us = pd.read_pickle("data/data_US.pkl")
target_by_sector = pd.read_pickle("data/target_by_sector.pkl")

# interseccion entre cedears e indice
data = pd.merge(data_us, data_arg, left_index=True, right_index=True)

# reajustar Weights manteniendo proporciones entre sectores
current_by_sector = data.groupby(["GICS Sector"]).sum(["Weight"])["Weight"]
factor = (100 / target_by_sector.sum()) * target_by_sector / current_by_sector

for sector, factor_value in factor.iteritems():
    data.loc[data["GICS Sector"] == sector, ["Weight"]] *= factor_value

# Agregar columna de ultimo precio de cierre
# data = add_current_price(data)  #guardo en disco para evitar perder tiempo descargando datos
data = pd.read_pickle("data/data_with_price.pkl")
