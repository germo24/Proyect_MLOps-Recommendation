import pandas as pd
from fastapi import FastAPI
import numpy as np

app = FastAPI()

data = pd.read_csv('Dataset/clean_data.csv')
data_model = pd.read_csv('Dataset/model_data.csv')

def time_format(x):
    return f'{ int(x//60)} h { int(x - 60* (x // 60 )) } m'


@app.get("/")
async def root():
    return {"message": "Welcome to my proyect. The API conecction is working on!"}

@app.get('/peliculas_idioma/{language}')
def peliculas_idioma(language:str):
    
    quantity = len(data.loc[data['original_language'] == language, 'id'].unique())
    
    return {'language': language, 'amount':quantity}

@app.get('/peliculas_duracion/{movie}')
def peliculas_duracion(movie:str):
    
    subdata = data.loc[(data['title'] == movie), ['runtime', 'release_year']]
    subdata['runtime'] = subdata['runtime'].apply(lambda x: time_format(x))
    duration = subdata['runtime']
    year = subdata['release_year']
    
    return {'movie': movie, 'coincidences': len(subdata),
            'duration': [i for i in duration], 'year': [i for i in year]}


@app.get('/franquicia/{franchise}')
def franquicia(franchise:str):

    subdata = data.loc[(data['belongs_to_collection'] == franchise), ['revenue']]
    n_movies = len(subdata)
    total_earn = int(subdata['revenue'].sum())
    average_earn = int(total_earn / n_movies)
    
    return {'franchise': franchise,
            'number of movies': n_movies,
            'total earn': total_earn,
            'average earn': average_earn}
    

@app.get('/peliculas_pais/{country}')
def peliculas_pais(country:str):
    
    subdata = data.copy()
    subdata['production_countries'] = subdata['production_countries'].apply(lambda x: str(x).split(', '))
    list_id = []

    for i in range(len(subdata)):
        if(country in subdata['production_countries'][i]): 
            list_id.append(subdata['id'][i])
            
    n_movies = len(set(list_id))
    
    return {'country': country, 'number of movies': n_movies}

@app.get('/productoras_exitosas/{company}')
def productoras_exitosas(company:str):
    
    subdata = data.copy()
    subdata['production_companies'] = subdata['production_companies'].apply(lambda x: str(x).split(', '))

    list_id = []
    total_revenue = 0

    for i in range(len(subdata)):
        if(company in subdata['production_companies'][i]):
            if subdata['id'][i] not in list_id:
                list_id.append(subdata['id'][i])
                total_revenue = total_revenue + subdata['revenue'][i]
                
    n_movies = len(list_id)
    total_revenue = int(total_revenue)

    return {'company': company,
            'Number of movies': n_movies,
            'total revenue': total_revenue}
    


@app.get('/get_director/{director_name}')
def get_director(director_name:str):
    
    subdata = data.copy()
    subdata['crew'] = subdata['crew'].apply(lambda x: str(x).split(', '))
    
    list_id = []
    movies = []
    total_return = 0

    for i in range(len(data)):
        if(director_name in subdata['crew'][i]):
            
            if subdata['id'][i] not in list_id:
                list_id.append(subdata['id'][i])
                total_return = total_return +  subdata['return'][i]
                movies.append({'title': str(subdata['title'][i]), 'date_release': str(subdata['release_year'][i]),
                            'return': str(subdata['return'][i]), 'budget': str(subdata['budget'][i]),
                            'revenue': str(subdata['revenue'][i])})
                
    return {'director': director_name, 'return': total_return, 'movies': movies}

@app.get('/recomendacion/{title}')
def recomendacion(title:str):
    model = data_model.copy()
    model['genres'] = model['genres'].apply(lambda x: str(x).split(', '))

    indice = model[model['title'] == title].index[0]
    generos = model['genres'][indice]

    coef = []

    for h in model['genres']:
        num = 0
        for m in generos:
                    
            if(m in h): num += 1
        coef.append(num)
    
    model['coef'] = coef
    model = model[['coef','popularity','vote_average']]
    X = model.values
    
    reference_point = X[:,0][indice], X[:,1][indice], X[:,2][indice]

    # Calcular la distancia euclidiana entre los puntos y el punto de referencia
    distances = np.linalg.norm(X - reference_point, axis=1)

    # Definir un radio de cercanía para los puntos
    radius = 1.5

    # Filtrar los puntos cercanos al punto de referencia
    nearby_points = X[distances < radius]
    
    ind_min = []
    for z,  i in enumerate(nearby_points):
        ind_min.append([sum(abs(reference_point - i)), z])
        
    ind_min.sort()
    ind_min = [i[1] for i in ind_min][1:6]
    
    points = nearby_points[ind_min]

    coordenadas = points[:, 1:]

    # Buscar los índices donde las coordenadas coinciden
    indices_coincidentes = np.where(np.isin(X[:, 1:], coordenadas).all(axis=1))[0]
    recomended_movies = data_model.loc[indices_coincidentes, 'title'].values
    recomended_movies = [str(i) for i in recomended_movies]
    
    return {'recomendend_movies': recomended_movies}
            
    