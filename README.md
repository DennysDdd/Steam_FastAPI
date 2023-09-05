# SteamFastAPI


### Este primer proyecto individual nos hará recorrer el ciclo de Machine Learning Operations, partiendo de un dataset de juegos de la plataforma Steam, hasta llegar a un modelo de Machine Learning de recomendacion de juegos, en este caso se eligio un modelo user-item.

<br>
<div style="text-align: right; color: violet; font-size: 1.2em; font-weight: bold;">
  <a href="https://github.com/DennysDdd/Steam_FastAPI.git" style="color: violet; text-decoration: none;">
    by Dennys Diaz Romero, Cohorte 14
  </a>
</div>

# <h1 align=center> **Introducción** </h1>

El desafío planteado en para este proyecto consiste en desarrollar un proceso de MLOs que incluya multiples etapas,tales como Ingenieria de datos con su correspondiente Extraction, Transform and Load (ETL), el Analasis Exploratotrio de los datos(EDA), pasando al Machine Learning , junto con la exploración y entrenamiento de modelos; finalizando con el deployment tanto del modelo como de los datos del proceso ETL y EDA.

# <h1 align=center> **Desarrollo del Proyecto**</h1>

## ETL/Ingeniería de Datos

En el rol de Data Engineer iniciamos el proceso de ETL. El proceso del mismo se encuentra detallado en el archivo de nombre `extraccion_db.ipynb` en el cual se analiza a profundidad cada dataframe consigna, trasnformandolo en data ideal para nuestros procesos:


+ Conversión a dataframe de los archivos consigna.
+ Búsqueda y observación de filas sin datos útiles (vacíos, datos inespecíficos, duplicados)
+ Eliminación de columnas que no van a ser útiles en aplicaciones posteriores.
+ Conversión de los tipos de datos  de columnas asignados por defecto a tipos adecuados.
+ Exploración de columnas con similitudes y sustitución de datos ausentes usando las similitudes mediante la imputación.
+ Eliminación de columnas redundantes(data repetida).
+ Exploración de Géneros y Sentiments con técnica one hot encoding, decisión respecto a las mismas.
+ Reemplazo de valores sin relación con la columna donde se encuentran por NAN o None.

## EDA

Nuevamente, el detalle de este proceso puede seguirse paso a paso en el Jupyter Notebook :

+ Iniciamos con la data **limpia** proveniente del proceso de ETL
+ Seleccion de uno de los dataframes *limpios* para poder realizar sus análsis de datos a profundidad.
+ Descarte de filas que no contienen precios (ya que precio será la variable a predecir por el modelo)
+ Primer observación matriz de correlación
+ Eliminación de filas que carecen de valores en las columnas seleccionadas para explorar modelos.
+ Reinicio del index y guardado del dataframe en archivo parquet, para ser consumido por el modelo.

## Proceso de Machine Learning

En este proceso se detalla el sistema de recomendación *collaboritive filtering* donde se usa el método del coseno y varias matrices de correlacion para la selección de ususarios símiles al ingresado


## Desarrollo de la aplicación de FAST API

### La misma consta de 3 funciones de validación de datos, 1 ruta raíz, 6 rutas de consulta de datos del dataset (endpoints), más la ruta de predicción de precio de juegos usando el modelo de Machine Learning.

```Python

@app.get("/user_data/{user_id}")
def user_data(user_id):
    """ Devuelve el dinero gastado por el usuario """

@app.get('/countereviews/{fecha1},{fecha2}')
def countreviews(fecha1: str, fecha2: str):
    """ Devuelve la cantidad de usuarios que hicieron un review entre dichas fechas """

@app.get('/genre/{genero}')
def genre(genero: str): 
    """ Devuelve el puesto del genero ingresado, dentro del ranking de generos """

@app.get('/userforgenre/{genero}')
def userforgenre(genero):
    """
    Esta funcion solicita un genero, y muestra los top 5 jugadores con mayor tiempo de juego de ese genero

    paramteres:
    genero: str

    Ejemplo:
    userforgenre(Action)

    """

@app.get('/developer/{desarrollador}')
def developer(desarrollador: str):
    """
    Esta funcion extrae el porcentaje de juegos que han sido Free(sin costo) por desarrollador y por año
    """

@app.get('/sentiment_analysis/{anio}')
def sentiment_analysis(anio: int):
    """
    Esta funcion devuelve los reviews por año

    parameters:
    anio:int

    Ejemplo:  sentiment_analysis(2011)
    """

@app.get('/recomienda_usuario/{id_usuario}')
def recomienda_usuario(id_usuario: str):
    return recomienda(id_usuario)


```

# <h1 align=center> **Entregables**</h1>


## Aplicación de FAST API - SteamFastApi

La aplicación se encuentra disponible en [la siguiente ubicación](https://steam-fastapi.onrender.com/). Tener en cuenta que Render apaga las aplicaciones, dar tiempo a que construya el contenedor y reinicie la app.


## Video

[Video]https://youtu.be/6Tv-eBoc4fY



