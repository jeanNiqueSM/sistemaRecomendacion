from flask import Flask, render_template, request, session, redirect, url_for
from modulo_sr import hacer_recomendaciones, lista_usuarios
from forms import SignUpForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'

"""Information regarding the Users in the System."""
users = [
            {"id": 1, "full_name": "Jean Ñique", "email": "admin@gmail.com", "password": "admin"},
        ]


@app.route('/')
def home():
    usuarios = lista_usuarios()
    return render_template('home.html', usuarios=usuarios)

@app.route('/about')
def about():
    return render_template('about.html', )


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

@app.route("/signup", methods=["POST", "GET"])
def signup():
    """View function for Showing Details of Each Pet."""
    form = SignUpForm()
    if form.validate_on_submit():
        new_user = {"id": len(users)+1, "full_name": form.full_name.data, "email": form.email.data, "password": form.password.data}
        users.append(new_user)
        return render_template("signup.html", message = "Registro exitoso")
    return render_template("signup.html", form = form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = next((user for user in users if user["email"] == form.email.data and user["password"] == form.password.data), None)
        if user is None:
            return render_template("login.html", form = form, message = "Email o contraseña. Intente nuevamente.")
        else:
            session['user'] = user
            return render_template("home.html", message = "Inicio de Sesión exitoso!")
    return render_template("login.html", form = form)

@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login', _scheme='', _external=True))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
