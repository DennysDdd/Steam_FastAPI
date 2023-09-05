from fastapi import FastAPI, Query
import pandas as pd
import numpy as np
from modelo_recomendacion import recomienda

# Instanciamos FastAPI
app = FastAPI()

df_games = pd.read_json("clean_games.json")
df_reviews = pd.read_parquet("clean_reviews.parquet")
df_items = pd.read_parquet("australian_users_items.parquet")
df_genres = pd.read_json("clean_genre.json")
df_lista_genre = pd.read_json("dataframe_genre.json")
df_playtime = pd.read_parquet("parquet_generos.parquet")


@app.get('/')
def root():
    """ Mensaje de bienvenida """

    return {"message": "Bienvenidos!"}


# Procedemos a definir el ETL de la lectura de los archivos, asi como algunas funciones utiles para los requerimientos


def cambiar_release(cadena_fecha):
    """
    Esta funcion extrae unicamente el año del release_date
    """
    if cadena_fecha == None:
        return None
    else:
        return cadena_fecha.split("-")[0]

# ETL DE DF_REDUCIDO


def cambiar_tipo(cadena):
    """
    Esta funcion ayuda a transformar los datos de un string para los diferentes casos, mostrando una data mas limpia
    """
    if (cadena == "play warmachine: tactics demo") or (cadena == 'free mod'):
        cadena = 0
    elif isinstance(cadena, str):
        try:
            cadena = float(cadena)
        except ValueError:
            cadena = 0
    elif isinstance(cadena, int) or isinstance(cadena, float):
        pass
    elif cadena == None:
        cadena = 0
    return cadena

# ETL DF_GAMES


def evaluar_presencia_user(user_id):
    if user_id != None:
        return True
    else:
        return False


def valida_anio(anio1, anio2):
    # Validamos que el año de 2 fechas sean consecuentes para evaluar en los filtros de la funcion counterreviews
    anio1 = int(anio1)
    anio2 = int(anio2)
    if anio1 > anio2:
        return True
    elif anio1 > 2023 or anio2 > 2023 or anio1 < 1950 or anio2 < 1950:
        return True
    else:
        return False


def trans_review(cadena):
    if type(cadena) != str:
        return str(cadena)
    else:
        return cadena


df_reviews_copia1 = df_reviews.copy()

# Ubicamos las filas donde  no se tenga informacion de posted
indices_2 = df_reviews_copia1["posted"][df_reviews_copia1["posted"].apply(
    lambda x: x == None)].index

# Para la consigna se trabaja unicamente los datos donde se conozca los años
df_reviews_copia1.drop(indices_2, inplace=True, axis=0)
df_reviews_copia1.reset_index(drop=True, inplace=True)

# Aqui estamos pasando a formato fecha
df_reviews_copia1["posted"] = pd.to_datetime(df_reviews["posted"])

# Creamos un nuevo dataframe DF_REVIEWS_COPIA1

# Reducimos el dataframe solo con las variables que necesitamos

df_reducido = df_games.loc[:, ["release_date", "price", "developer"]]
df_reducido["release_date"] = df_reducido["release_date"].apply(
    lambda x: cambiar_release(x))

# CREAMOS OTRO DATAFRAME EN BASE A GAMES

# Creamos un dataframe DF_COPIA2
df_reviews_copia2 = df_reviews.copy()
df_reviews_copia2["posted"] = df_reviews_copia2["posted"].apply(
    lambda x: cambiar_release(x))
df_reviews_copia2 = df_reviews_copia2.dropna(subset=["posted"])
df_reviews_copia2.reset_index(drop=True, inplace=True)
df_reviews_copia2["posted"] = df_reviews_copia2["posted"].apply(
    lambda x: trans_review(x))


# Un decorador modifica la funcion a la que le sigue


@app.get('/')
def root():
    """ Mensaje de bienvenida """
    return {"message": "Bienvenidos a la FastAPI!"}


@app.get("/user_data/{user_id}")
def user_data(user_id):
    ''' Esta funcion retornara la cantidad de dinero que el usuario gasto en los juegos de steam, además devolvera un porcentaje de recomendaciones
      en base a la cantidad de items(juegos) que posea

      parameters:

        user_id : id del usuario
    '''
    if evaluar_presencia_user(user_id):
        user_id = str(user_id)

        # cantidad_items = df_items[df_items["user_id"]==user_id].shape[0]
        data = df_items[df_items["user_id"] == user_id]
        cantidad_juegos = data.shape[0]
        mascara = data["item_id"].isin(df_games["id"])

        # Aca observamos la cantidad de juegos del dataframe df_games que coinciden con los registros de data_items
        juegos = data[mascara]

        # filas en las que se tiene la concidencia por id del item
        indices = np.where(df_games['id'].isin(juegos["item_id"]))[0]

        precio_juegos = df_games.loc[indices, "price"]
        gasto = sum(precio_juegos)

        # Con esto accederemos a los reviews del usuario
        review_usuario = df_reviews[df_reviews["user_id"] == user_id]

        # Uso  el dataframe juegoss["item_id"] para filtrar los juegos que tienen recommend

        mascara3 = review_usuario["item_id"].isin(juegos["item_id"])
        commend_filas = review_usuario[mascara3]

        # Se vuelve a hacer este filtrado pues se requiere certificar si realmente los juegos que coinciden entre los que el usuario tiene son la misma cantidad
        # Que los que haya hecho review

        suma_recommends = 0
        for i in range(commend_filas.shape[0]):
            if commend_filas.iloc[i, 4] != None:
                suma_recommends += commend_filas.iloc[i, 4]
        # Sumamos las recomendaciones, sabiendo los elementos True y False son tomados como elementos binario en la suma
        try:
            porcentaje = (suma_recommends/cantidad_juegos)*100
        except ZeroDivisionError:
            porcentaje = 0

        return f"""La cantidad de dinero gastado por el usuario {user_id} es: {round(gasto,3)}
El porcentaje de recomendación en base a su cantidad de items de: {cantidad_juegos} es {porcentaje}%"""

    else:
        return "Este usuario no existe"


@app.get('/countereviews/{fecha1},{fecha2}')
def countreviews(fecha1: str, fecha2: str):
    """Esta funcion retornara la cantidad de usuarios y el porcentaje de recomendaciones entre 2 fechas específicas.

       parameters:
       fecha1: fecha inicial(start) con formato YYYY-MM-DD
       fecha2: fecha final(end) con formato YYYY-MM-DD
    """
    # Validamos las fechas que se ingresan
    lista_fecha1 = fecha1.split("-")
    lista_fecha2 = fecha2.split("-")
    if valida_anio(lista_fecha1[0], lista_fecha2[0]):
        return "Fechas Incorrectas"
    elif (int(lista_fecha1[0]) == int(lista_fecha2[0])) and (int(lista_fecha1[1]) > int(lista_fecha2[1])):
        return "Fechas Incorrectas"
    elif (int(lista_fecha1[0]) == int(lista_fecha2[0])) and (int(lista_fecha1[1]) == int(lista_fecha2[1])) and (int(lista_fecha1[2]) > int(lista_fecha2[2])):
        return "Fechas Incorrectas"
    else:
        filas = df_reviews_copia1["posted"][(df_reviews_copia1["posted"] > fecha1) & (
            df_reviews_copia1["posted"] < fecha2)].index
        df_rango_fechas = df_reviews_copia1.loc[filas, :]
        cantidad_personas = df_rango_fechas.shape[0]
        recommends = sum(
            df_rango_fechas["recommend"][df_rango_fechas["recommend"] == True])
        try:
            porcentaje = (recommends/cantidad_personas)*100
        except ValueError:
            return f"""La cantidad de usuarios entre las fechas {fecha1} y {fecha2} es: {cantidad_personas},
        ademas el porcentaje de recomendacion es 0%"""
        except ZeroDivisionError:
            return f"""La cantidad de usuarios entre las fechas {fecha1} y {fecha2} es: {cantidad_personas},
        ademas el porcentaje de recomendacion es 0%"""

        else:
            return f"""La cantidad de usuarios entre las fechas {fecha1} y {fecha2} es: {cantidad_personas},
ademas el porcentaje de recomendacion es {porcentaje}%"""


@app.get('/genre/{genero}')
def genre(genero: str):
    """
    Esta funcion devuelve el puesto en el que se encuentra dicho genero
    """

    if genero in df_lista_genre["genre"].values:
        filtro = df_lista_genre["playtime_forever(minutes)"][df_lista_genre["genre"] == genero]
        puesto = filtro.index[0]
        horas = filtro.values[0]
        return f"El puesto de {genero} es {puesto}, con {horas} horas"

    else:
        return "Este genero no existe"


@app.get('/userforgenre/{genero}')
def userforgenre(genero):
    """
    Esta funcion solicita un genero, y muestra los top 5 jugadores con mayor tiempo de juego de ese genero

    paramteres:
    genero: str

    Ejemplo:
    userforgenre(Action)

    """
    genero = "genre_"+genero
    if genero in df_playtime.columns:

        resultado = df_playtime
        # Procedemos a  sacar el top de usuarios que hayan jugado mas por genero
        resultado.sort_values(by="playtime_forever",
                              ascending=False, inplace=True)
        users = resultado.iloc[0:5, :].loc[:, [
            "user_id", "user_url", "playtime_forever"]]
        dicciona = users.to_dict(orient="records")

        return dicciona
    else:
        return "Lo siento, ningun juego tiene este género"


@app.get('/developer/{desarrollador}')
def developer(desarrollador: str):
    """
    Esta funcion extrae el porcentaje de juegos que han sido Free(sin costo) por desarrollador y por año
    """
    df_desarrollador = df_reducido[df_reducido["developer"] == desarrollador]
    fechas = df_desarrollador["release_date"].unique()

    # Creamos un diccionario con los pares años, y precios
    diccionario_anios = {}
    diccionario_tamanio = {}
    for i in fechas:
        df_free = df_desarrollador[df_desarrollador["release_date"] == i]
        diccionario_anios[i] = len(df_free[df_free["price"] == 0])
        diccionario_tamanio[i] = df_free.shape[0]

    # Se extrae la cantidad de items en total, y aquellos que no son free

    diccionario_cantidades = {}

    for i in diccionario_anios:
        try:
            diccionario_cantidades[i] = (
                diccionario_anios[i]/diccionario_tamanio[i])*100
        except ZeroDivisionError:
            diccionario_cantidades[i] = 0

    # Se muestra el porcentaje de juegos free del desarrollador por año
    df_mostrar = pd.DataFrame({'años': diccionario_cantidades.keys(
    ), "Porcentaje Free(%)": diccionario_cantidades.values()})
    return df_mostrar


@app.get('/sentiment_analysis/{anio}')
def sentiment_analysis(anio: int):
    """
    Esta funcion devuelve los reviews por año

    parameters:
    anio:int

    Ejemplo:  sentiment_analysis(2011)
    """
    try:

        if anio <= 2015:
            anio = str(anio)
            seleccionado = df_reviews_copia2[df_reviews_copia2["posted"] == anio]
            resultado = seleccionado["review"].value_counts()
            resultado = resultado.to_dict()
            return dict(zip(["Neutro", "Positivo", "Negativo"], resultado.values()))
        else:
            return "No hay data de ese año"
    except Exception as e:
        return {"error": str(e)}


@app.get('/recomienda_usuario/{id_usuario}')
def recomienda_usuario(id_usuario: str):
    return recomienda(id_usuario)
