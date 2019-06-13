from flask import Flask, render_template, request, url_for, redirect
from flaskext.mysql import MySQL
from os import path, makedirs
from werkzeug.utils import secure_filename
from bd import *

app = Flask(__name__)
bd = MySQL()
bd.init_app(app)

upload_dir = ('static')
makedirs(upload_dir, exist_ok=True)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'concessionaria'


# verificar se o funcionário está logado type 1 = gerente / type 0 = vendedor
login_type = None
login_name = None

@app.route('/')
def home(erro=None):
    conn = bd.connect()
    cursor = conn.cursor()
    vips = show_vips(cursor)
    cursor.close()
    conn.close()
    return render_template('home.html', vips=vips, logado=login_type, erro=erro)


@app.route('/cadastro_carro')
def insercao(erro=None):
    if login_type:
        return render_template('inserir.html', erro=erro)
    else:
        erro = 'Por favor efetuar login'
        return redirect(url_for('login_template', erro=erro))


@app.route('/inserir_carro', methods=['post'])
def inserir():
    foto = request.files['foto']
    marca = request.form.get('marca')
    modelo = request.form.get('modelo')
    placa = request.form.get('placa')
    vip = request.form.get('vip')
    preco = request.form.get('preco')
    if vip is None:
        vip = 0
    conn = bd.connect()
    cursor = conn.cursor()
    foto.save(path.join(upload_dir, secure_filename(foto.filename)))
    vips = vip_verifie(cursor)
    if vips >= 10:
        alerta = 'Não é possível adicionar mais de 10 carros como VIP'
        cursor.close()
        conn.close()
        return redirect(url_for('incersao', erro=alerta))
    set_car(conn, cursor, marca, modelo, foto.filename, preco, placa, vip)
    cursor.close()
    conn.close()
    return redirect(url_for('insercao'))


@app.route('/login')
def login_template(erro=None):
    return render_template('login.html', erro=erro)


@app.route('/validate_login', methods=['post'])
def login():
    user = request.form.get('user')
    passwd = request.form.get('pass')
    conn = bd.connect()
    cursor = conn.cursor()
    usuario = validate_login(cursor, user, passwd)
    cursor.close()
    conn.close()
    global login_type
    global login_name
    login_type = usuario[0]
    login_name = usuario[1]
    if login_type == 0:
        return redirect(url_for('home_vendedor'))
    elif login_type == 1:
        return redirect(url_for('home_gerente'))
    else:
        erro = 'Login e Senha não conferem!'
        return redirect(url_for('login_template.html', erro=erro))


@app.route('/user/gerente')
def home_gerente():
    if login_type == 1:
        return render_template('gerente.html', nome=login_name)
    elif login_type == 0:
        return redirect(url_for('home_vendedor', nome=login_name))
    else:
        return redirect(url_for('home'))


@app.route('/user/vendedor')
def home_vendedor():
    if login_type == 0:
        return render_template('vendedor.html', nome=login_name)
    elif login_type == 1:
        return redirect(url_for('home_gerente', nome=login_name))
    else:
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    global login_name
    global login_type
    login_type = None
    login_name = None
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)