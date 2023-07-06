import pandas as pd
from fastapi import FastAPI

app = FastAPI()

data = pd.read_csv('Dataset/clean_data.csv')

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
            
    