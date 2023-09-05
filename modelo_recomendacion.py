import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise

df_reviews = pd.read_parquet("clean_reviews.parquet")
df_reviews.drop(["posted", "user_url"], axis=1, inplace=True)


# Este sera mi "dataframe" donde veremos la interseccion entre usuarios y juegos, y el valor de interseccion sera el review analizado con analysis_sentiments
df_matrix = pd.pivot_table(df_reviews, values="review",
                           index="item_id", columns="user_id").fillna(0)
ratings = df_matrix.values

# Separamos los valores de la matriz de relacion:
ratings_train, ratings_test = train_test_split(
    ratings, test_size=0.2, random_state=42)

# Ahora como estara la similitud entre usuarios
sim_amtrix = 1-pairwise.cosine_distances(df_matrix.values)

# Para poder operar con los valores de la matriz de relacion de user-based, es necesario usar matrices cuadrados, para ello tomamos:
size = min(sim_amtrix.shape[0], sim_amtrix.shape[1])
# Se toma el valor minimo entre el tamaño de la matriz de similitud entre usuarios
test_size = 737
train_size = size-test_size

# Separamos la data de sim_amtrix en funcion del tamaño de nuestra muestra de separacion de rating_train y test

sim_amtrix_train, sim_amtrix_test = train_test_split(
    sim_amtrix, train_size=train_size, test_size=test_size, random_state=42)
sim_amtrix_train = sim_amtrix[0:2945, 0:2945]
sim_amtrix_test = sim_amtrix[2945:, 2945:]

# Procedemos a la prediccion de similitud:
prediccion = (sim_amtrix_train).dot(ratings_train) / \
    np.array([np.abs(sim_amtrix_train).sum(axis=1)]).T


dataaframe = pd.DataFrame(prediccion.argsort().T)
# Con esta matriz ubicamos facilmente los usuarios
dataaframe.index = df_matrix.columns


def recomienda(usuario):
    """
    Esta funcion muestra la lista de los 5 id de juegos que podrian gustarle al usuario ingresado
    """
    user0 = dataaframe.loc[usuario, :]

    # Las 5 recomendaciones  con mayor puntaje es:
    diccion = {}
    for i, a in enumerate(user0[-5:]):
        diccion[i+1] = {a}
    return diccion


# usuario = "LydiaMorley"
# usuario =  "js41637"


# Veamos el porcentaje de error de nuestro sistema de recomendacion:

def mse(preds, actuals):
    if preds.shape[1] != actuals.shape[1]:
        actuals = actuals.T
    preds = preds[actuals.nonzero()].flatten()
    actuals = actuals[actuals.nonzero()].flatten()
    return mean_squared_error(preds, actuals)


medida_train = mse(prediccion, ratings_train)

# Realizamos la recomendacion para nuestro set de testeo
pred_test = (sim_amtrix_test).dot(ratings_test) / \
    np.array([np.abs(sim_amtrix_test).sum(axis=1)]).T

medida_test = mse(pred_test, ratings_test)
