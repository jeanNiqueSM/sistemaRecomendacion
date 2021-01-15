#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os
#get_ipython().run_line_magic('matplotlib', 'inline')

from sklearn.neighbors import NearestNeighbors



# In[2]:

ruta_db = os.path.join(os.getcwd(), "database")
usuarios = pd.read_excel(os.path.join(ruta_db, "datasets_usuarios.xlsx"))
recursos = pd.read_excel(os.path.join(ruta_db, "datasets_recursos.xlsx"))


# In[3]:


#print(usuarios.head())
#print('-'*120)
#print(recursos.head())


# ## EXPLORANDO LOS DATOS PARA LA TABLA "USUARIOS" 

# In[4]:


# ELIMINANDO LAS COLUMNAS QUE NO NECESITAREMOS
usuarios_copy = usuarios.copy()
cols_usuarios = ["USER_ID", "SUBJECTS_OF_INTEREST", "RATING", "EVALUATION_DATE", "SUBJECT", "TITLE", 
                              "URL", "LO_OBJ_ID", "RESOURCE_TYPE", "MIN_AGE", "MAX_AGE"]
usuarios_copy = usuarios_copy[cols_usuarios]

# CAMBIANDO EL NOMBRE A LAS COLUMNAS
usuarios_copy.rename(columns={"USER_ID":"user_id", "SUBJECTS_OF_INTEREST": "tema_interes", "RATING": "calificacion", 
                              "EVALUATION_DATE": 'fecha_evaluacion', "SUBJECT": "tema", "TITLE": "titulo", "URL": 'url', 
                              "LO_OBJ_ID": 'recurso_id', "RESOURCE_TYPE": "tipo_recurso", "MIN_AGE": "edad_minima", 
                              "MAX_AGE": "edad_maxima"}, inplace=True)

#print(usuarios_copy.head())


# In[5]:


# CONVIRTIENDO LA COLUMNA 'user_id' DE INT A OBJECT
usuarios_copy['user_id'] = usuarios_copy['user_id'].astype(str).str.replace('.0','')

# CONVIRTIENDO LA COLUMNA 'id_recurso' DE INT A OBJECT
usuarios_copy['recurso_id'] = usuarios_copy['recurso_id'].astype(str).str.replace('.0','')

# REEMPLAZANDO VALORES NULOS DE LA COLUMNA 'tema' POR LA PALABRA GENERAL
usuarios_copy['tema'].fillna("General", inplace=True)

# REEMPLAZANDO VALORES NULOS DE LA COLUMNA 'tema_interes' POR LA PALABRA GENERAL
usuarios_copy['tema_interes'].fillna("General", inplace=True)


# In[6]:


edades_min_prom = round(np.arange(10,16).mean())
usuarios_copy['edad_minima'].fillna(edades_min_prom, inplace=True)

# CONVIRTIENDO LA COLUMNA 'edad_minima' DE FLOAT A INT
usuarios_copy['edad_minima'] = usuarios_copy['edad_minima'].astype(int)

edades_max_prom = int(round(np.arange(15,20).mean()))

# REEMPLAZANDO LOS VALORES DE CADENA A VACÍO
usuarios_copy['edad_maxima'] = usuarios_copy['edad_maxima'].str.replace('"','')
usuarios_copy['edad_maxima'] = usuarios_copy['edad_maxima'].str.replace('120', str(edades_max_prom))
usuarios_copy['edad_maxima'] = usuarios_copy['edad_maxima'].replace('', np.nan)

# REEMPLAZANDO VALORES NULOS
usuarios_copy['edad_maxima'].fillna(edades_max_prom, inplace=True)

# ELIMINANDO LAS FILAS CON VALORES NULOS
usuarios_copy.dropna(inplace=True)

#  CONVIRTIENDO LOS VALORES DE LA COLUMNA edad_maxima DE OBJECT A ENTERO
usuarios_copy['edad_maxima'] = usuarios_copy['edad_maxima'].astype(int)

usuarios_copy['edad_prom'] = round((usuarios_copy['edad_minima'] + usuarios_copy['edad_maxima'])/2).astype(int)

cond_edad_prom = (usuarios_copy['edad_prom'] >= 10) & (usuarios_copy['edad_prom'] < 20)
usuarios_copy = usuarios_copy[cond_edad_prom]

# COLUMNAS A TRABAJAR
cols_modelado = ['user_id', 'recurso_id', 'calificacion']
usuarios_modelado = usuarios_copy[cols_modelado].reset_index(drop=True)
usuarios_modelado.head()


# ## EXPLORACION Y LIMPIEZA DE DATOS PARA LA TABLA "RECURSOS"

# In[7]:


# HACEMOS UNA COPIA DEL DATAFRAME DE RECURSOS
recursos_copy = recursos.copy()

# FILTRANDO LAS COLUMNAS QUE VAMOS A NECESITAR
cols_recursos = ['RESULT_LRE_ID', 'SUBJECTS_OF_INTEREST', 'INSERTION_TIMESTAMP', 'SUBJECT', 
                'TITLE', 'URL']

recursos_copy = recursos_copy[cols_recursos]

# CAMBIANDO EL NOMBRE A LAS COLUMNAS
recursos_copy.rename(columns={'RESULT_LRE_ID': 'recurso_id', 'SUBJECTS_OF_INTEREST': 'tema_interes', 
                              'INSERTION_TIMESTAMP': 'fecha_ingreso', 'SUBJECT': 'tema', 
                              'TITLE': 'titulo', 'URL': 'url'}, inplace=True)


# recursos_copy.head()


# In[8]:


# CAMBIANDO EL TIPO DE DATO DE LA COLUMNA 'recurso_id' DE NUMÉRICO A OBJECT
recursos_copy['recurso_id'] = recursos_copy['recurso_id'].astype(str)

# LOS VALORES NULOS PARA LAS COLUMNAS 'tema_interes' Y 'tema' LO REEMPLAZAREMOS POR 'General'
recursos_copy['tema_interes'].fillna('General', inplace=True)
recursos_copy['tema'].fillna('General', inplace=True)

# RECURSOS PARA EL ESTUDIO
cols_modelado_recurso = ['recurso_id', 'titulo']
recursos_modelado = recursos_copy.drop_duplicates(cols_modelado_recurso, keep='last')
recursos_modelado = recursos_modelado[cols_modelado_recurso].reset_index(drop=True)
recursos_modelado.head()


# In[9]:


# COMBINANDO LAS TABLAS "usuarios_modelado" Y "recursos_modelado"
ranking = pd.merge(usuarios_modelado, recursos_modelado, on='recurso_id')

# CONSTRUYENDO UNA TABLA PIVOTE PARA LOS TITULOS DE LOS CURSO Y ID DE USUARIOS
recursos_rating = ranking.pivot_table(index=['titulo'], columns=['user_id'], values='calificacion').T


# In[10]:


rate = {}
rows_indexes = {}
for i, row in recursos_rating.iterrows():
    rows = [x for x in range(0, len(recursos_rating.columns))]
    combine = list(zip(row.index, row.values, rows))
    rated = [(x,z) for x,y,z in combine if str(y) != 'nan']
    index = [i[1] for i in rated]
    row_names = [i[0] for i in rated]
    rows_indexes[i] = index
    rate[i] = row_names


# In[11]:


pivot_table = ranking.pivot_table(values='calificacion', index='user_id', columns='titulo').fillna(0)
pivot_table = pivot_table.apply(np.sign)

# Recursos no calificados por el usuario
no_calif = {}
no_calif_indexs = {}
for i, row in recursos_rating.iterrows():
    rows = [x for x in range(0, len(recursos_rating.columns))]
    combine = list(zip(row.index, row.values, row))
    idx_row = [(idx, col) for idx, val, col in combine if not val > 0]
    indices = [i[1] for i in idx_row]
    row_names = [i[0] for i in idx_row]
    no_calif_indexs[i] = indices
    no_calif[i] = row_names


# In[12]:


# Recomendacion KNearestNeighbors
n = 30
modelo_nn = NearestNeighbors(n_neighbors=n, algorithm='brute', metric='cosine')
recurso_nn_fit = modelo_nn.fit(pivot_table.T.values)
item_distancias, item_indices = recurso_nn_fit.kneighbors(pivot_table.T.values)

# Recomendacion basada en recursos
rec_dict = {}
for i in range(len(pivot_table.T.index)):
    rec_idx = item_indices[i]
    col_names = pivot_table.T.index[rec_idx].tolist()
    rec_dict[pivot_table.T.index[i]] = col_names
    
# Recomendación TOP (defiendo cantidad de elementos a recomendar) de los recursos 
top_recs = {}
for k,v in rows_indexes.items():
    item_idx = [j for i in item_indices[v] for j in i]
    item_dist = [j for i in item_distancias[v] for j in i]
    combine = list(zip(item_dist, item_idx))
    dictionary = {i:d for d,i in combine if i not in v}
    zipped = list(zip(dictionary.keys(), dictionary.values()))
    sort = sorted(zipped, key=lambda x: x[1])
    recomendaciones = [(pivot_table.columns[i], d) for i, d in sort]
    top_recs[k] = recomendaciones


# In[13]:


def hacer_recomendaciones(user, nmro_recom):
    list_rec = []
    lista_recursos = []
    print(f"Para el usuario {user} recomendamos estos cursos:\n")
    
    for k,v in top_recs.items():
        if user == k:
            for i in v[:nmro_recom]:
                print("{} con similaridad {:.4f}".format(i[0], 1-i[1]))
                list_rec.append(i[0])

    print("lista parcial", list_rec)

    for i in range(len(list_rec)):
        id_rec = recursos_modelado[(recursos_modelado['titulo']==list_rec[i])]['recurso_id'].values[0]
        mi_list = recursos_copy[recursos_copy['recurso_id'] == id_rec].reset_index(drop=True).values[0].tolist()
        lista_recursos.append(mi_list)

    print("lista final", lista_recursos)

    return lista_recursos


# In[14]:


# Recomendaciones Top: 
#mis_rec = hacer_recomendaciones('128')
#print('*'*100)
#print(mis_rec)
#def datos_recursos(list_rec):
#    lista_recursos = []
#    for i in range(len(list_rec)):
#        id_rec = recursos_modelado[(recursos_modelado['titulo']==mis_rec[i])]['recurso_id'].values[0]
#        mi_list = recursos_copy[recursos_copy['recurso_id'] == id_rec].reset_index(drop=True).values[0].tolist()
#        lista_recursos.append(mi_list)
#    return lista_recursos



