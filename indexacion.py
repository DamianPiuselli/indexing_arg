import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from parsing import add_current_price, ytd_prices

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
# Agrego precio por cedear en usd
data["Precio por CEDEAR"] = data["Price"] / data["Ratio"]


def portafolio(data, monto):
    # distribucion target de capital
    data = data.copy()
    data["TARGET"] = (data["Weight"] * monto) / (100 * data["Precio por CEDEAR"])

    # trackeo partes enteras y fraccionales
    data["Portafolio"] = data["TARGET"] // 1
    data["FRACCION"] = data["TARGET"] % 1
    capital_alocado = (data["Portafolio"] * data["Precio por CEDEAR"]).sum()
    capital_disponible = monto - capital_alocado

    # Proceso iterativo para eliminar las partes fraccionales
    while True:
        if capital_disponible < data["Precio por CEDEAR"].min():
            break
        else:
            posibles = data[data["Precio por CEDEAR"] < capital_disponible]
            eleccion = posibles[posibles["FRACCION"] == posibles["FRACCION"].max()]
            data.loc[eleccion.index, ["Portafolio"]] += 1
            data.loc[eleccion.index, ["FRACCION"]] = 0
            capital_alocado = (data["Portafolio"] * data["Precio por CEDEAR"]).sum()
            capital_disponible = monto - capital_alocado
    # borro columnas innecesarias
    data = data.drop(columns=["TARGET", "FRACCION"])
    return data


def portafolio_vs_index(portafolio):
    ytd_data = ytd_prices(portafolio)
    prices = pd.DataFrame()

    for ticker in ytd_data:
        try:
            prices[ticker] = (
                ytd_data[ticker]
                * portafolio["Portafolio"][ticker]
                / portafolio["Ratio"][ticker]
            )
        except KeyError:
            print(f"{ticker} no existe en el portafolio, ignorando")

    prices_series = prices.sum(axis=1)
    # ploteo el valor del portafolio vs spy

    plt.plot(prices_series / prices_series.iloc[0], label="Portafolio")
    plt.plot(ytd_data["SPY"] / ytd_data["SPY"].iloc[0], label="Index")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    # portafolio ejemplo.
    test = portafolio(data, 1000)
    portafolio_vs_index(test)
    # print(test[portafolio_test["Portafolio"] > 0])

