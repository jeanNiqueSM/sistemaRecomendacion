from modulo_sr import hacer_recomendaciones


def datos_recursos(lista_recursos):
    lista_recursos = []
    for i in range(len(lista_recursos)):
        id_rec = recursos_modelado[(recursos_modelado['titulo']==mis_rec[i])]['recurso_id'].values[0]
        mi_list = recursos_copy[recursos_copy['recurso_id'] == id_rec].reset_index(drop=True).values[0].tolist()
        lista_recursos.append(mi_list)
    return lista_recursos