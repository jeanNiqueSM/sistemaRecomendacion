from flask import Flask, render_template, request
from modulo_sr import hacer_recomendaciones

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/recomendacion', methods=['GET', 'POST'])
def recomendacion():
    if request.method == 'POST':
        id_usuario = request.form['id_usuario']
        nmro_rec = request.form['nmro_recursos']
        nmro_rec = int(nmro_rec)
    print("id usuario: ", id_usuario)
    print("nmro_rec: ", nmro_rec)
    print("tipo", type(nmro_rec))
    list_rec = hacer_recomendaciones(id_usuario, nmro_rec)
    return render_template('recomendacion.html', list_rec=list_rec, id_usuario=id_usuario)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
