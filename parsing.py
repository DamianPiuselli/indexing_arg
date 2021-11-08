import pandas as pd
from urllib import request
from urllib.request import Request, urlopen
import ssl


def convertir_ratio(string):
    """convierte el ratio de una string a:b a un float a/b"""
    [a, b] = string.split(":")
    return float(a) / float(b)


## Parseo de wikipedia. Tickers, Empresas, Sectores, reports.
## Parseo de slickcharts. Componentes.


def parsing_wikipedia():
    # leer contenido https sin contexto.
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    context = ssl._create_unverified_context()
    response = request.urlopen(url, context=context)
    html = response.read()
    return pd.read_html(html)[0]


def parsing_slickcharts():
    # leer contenido https, con crawler bloqueado. Emular browser.
    req = Request(
        "https://www.slickcharts.com/sp500",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    webpage = urlopen(req).read()
    return pd.read_html(webpage)[0]


def parsing_cedears():
    # leer contenido https sin contexto.
    url = "https://www.comafi.com.ar/2254-CEDEAR-SHARES.note.aspx"
    context = ssl._create_unverified_context()
    response = request.urlopen(url, context=context)
    html = response.read()

    data = pd.read_html(html)[0]
    # dropear datos innecesarios
    data = data.drop(
        columns=[
            "Programa de CEDEAR",
            "Alcance Público Inversor",
            "Código Caja de Valores",
            "CUSIP No.",
            "Mercado de Origen",
            "Frecuencia de Pago de Dividendo",
        ]
    )
    # renombrar campos
    data = data.rename(
        columns={
            "Símbolo BYMA": "Symbol BYMA",
            "Ticker en Mercado de Origen": "Symbol",
            "Ratio CEDEARs/valor subyacente": "Ratio",
        }
    )
    # setear index a ticker
    data = data.set_index("Symbol")
    ##correcciones a los datos
    # ticker BRK/B --> BRK.B
    data = data.rename(index={"BRK/B": "BRK.B"})

    # convertir Ratio de una string a un float
    data["Ratio"] = data["Ratio"].apply(convertir_ratio)

    return data


def main_data():
    # datos
    data = parsing_wikipedia()
    componentes = parsing_slickcharts()
    # mergear datos por ticker
    new = pd.merge(data, componentes, on="Symbol")
    # dropear datos innecesarios
    new = new.drop(
        columns=[
            "Company",
            "SEC filings",
            "Headquarters Location",
            "Date first added",
            "Founded",
            "#",
            "Price",
            "Chg",
            "% Chg",
        ]
    )
    # setear index a ticker
    new = new.set_index("Symbol")

    ##correcciones a los datos
    # Ignorar sector real estate (no hay cedears disponibles para REITS)
    # Ignorar utilities (no hay cedears disponibles)
    new = new[new["GICS Sector"] != "Real Estate"]
    new = new[new["GICS Sector"] != "Utilities"]

    # mergear 2 tipos de acciones de google GOOGL -> GOOG+GOOGL
    new.loc["GOOGL", "Weight"] = new.loc["GOOG", "Weight"] + new.loc["GOOGL", "Weight"]
    new = new.drop("GOOG")

    return new


if __name__ == "__main__":
    # datos
    data = main_data()
    data_c = parsing_cedears()
    target_weight_by_sector = data.groupby(["GICS Sector"]).sum(["Weight"])["Weight"]
    # guardar datos
    data.to_pickle("data/data_US.pkl")
    data_c.to_pickle("data/data_ARG.pkl")
    target_weight_by_sector.to_pickle("data/target_by_sector.pkl")
