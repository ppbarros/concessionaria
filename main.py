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
app.config['MYSQL_DATABASE_PASSWORD'] = 'GabiPP!7)9!7'
app.config['MYSQL_DATABASE_DB'] = 'concessionaria'



# verificar se o funcionário está logado type 1 = gerente / type 0 = vendedor
login_type = None
login_name = None

fconn = bd.connect()
fcursor = fconn.cursor()
create_first_user(fconn, fcursor)
fcursor.close()
fconn.close()


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
        return render_template('inserir.html', erro=erro, logado=login_type)
    else:
        erro = 'Por favor efetuar login'
        return redirect(url_for('login_template', erro=erro, logado=login_type))


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
    if vips > 10 and vip == '1':
        alerta = 'Não é possível adicionar mais de 10 carros como VIP'
        cursor.close()
        conn.close()
        return redirect(url_for('insercao', erro=alerta, logado=login_type))
    else:
        set_car(conn, cursor, marca, modelo, foto.filename, preco, placa, vip)
        cursor.close()
        conn.close()
        return redirect(url_for('insercao', logado=login_type))


@app.route('/login')
def login_template(erro=None):
    return render_template('login.html', erro=erro, logado=login_type)


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
    if usuario is None:
        erro = 'Login e Senha não conferem!'
        return redirect(url_for('login_template', erro=erro, logado=login_type))
    login_type = usuario[0]
    login_name = usuario[1]
    if login_type == 0:
        return redirect(url_for('home_vendedor', logado=login_type))
    elif login_type == 1:
        return redirect(url_for('home_gerente', logado=login_type))
    else:
        erro = 'Login e Senha não conferem!'
        return redirect(url_for('login_template', erro=erro, logado=login_type))


@app.route('/user/gerente')
def home_gerente():
    if login_type == 1:
        return render_template('gerente.html', nome=login_name, logado=login_type)
    elif login_type == 0:
        return redirect(url_for('home_vendedor', nome=login_name, logado=login_type))
    else:
        return redirect(url_for('home'))


@app.route('/user/vendedor')
def home_vendedor():
    if login_type == 0:
        return render_template('vendedor.html', nome=login_name, logado=login_type)
    elif login_type == 1:
        return redirect(url_for('home_gerente', nome=login_name, logado=login_type))
    else:
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    global login_name
    global login_type
    login_type = None
    login_name = None
    return redirect(url_for('home'))


@app.route('/reservar/<idcarros>')
def reservar(idcarros):
    return render_template('reservar.html', idcarros=idcarros)

@app.route('/efetuar_reserva/<idcarros>', methods=['post'])
def efetuar_reserva(idcarros):
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    tel = request.form.get('tel')
    conn = bd.connect()
    cursor = conn.cursor()
    reservar_carro(conn, cursor, nome, cpf, tel, idcarros)
    cursor.close()
    conn.close()
    return redirect(url_for('home'))


@app.route('/relatorio')
def all_cars():
    if login_type:
        conn = bd.connect()
        cursor = conn.cursor()
        carros = show_all_cars(cursor)
        cursor.close()
        conn.close()
        return render_template('relatorio.html', carros=carros, logado=login_type)
    else:
        return redirect(url_for('home'))


@app.route('/alterar_carro')
def available_cars(erro=None):
    if login_type:
        conn = bd.connect()
        cursor = conn.cursor()
        carros = show_available_cars(cursor)
        cursor.close()
        conn.close()
        return render_template('alterar_carro.html', carros=carros, logado=login_type, erro=erro)
    else:
        return redirect(url_for('home'))


@app.route('/cadastrar_usuario')
def cadastro_user():
    if login_type == 1:
        return render_template('inserir_user.html', logado=login_type)
    else:
        return redirect(url_for('home'))


@app.route('/cadastro_user', methods=['post'])
def inserir_user():
    user = request.form.get('login')
    senha = request.form.get('passwd')
    nome = request.form.get('nome')
    tipo = request.form.get('tipo')
    conn = bd.connect()
    cursor = conn.cursor()
    create_user(conn, cursor, user, senha, tipo, nome)
    cursor.close()
    conn.close()
    return redirect(url_for('home'))


@app.route('/limpar_reserva/<idcarros>')
def excluir_reserva(idcarros):
    if login_type:
        conn = bd.connect()
        cursor = conn.cursor()
        limpar_reserva(conn, cursor, idcarros)
        cursor.close()
        conn.close()
        return redirect(url_for('available_cars'))
    else:
        return redirect(url_for('home'))


@app.route('/tornar_vip/<idcarros>')
def tornar_vip(idcarros):
    if login_type:
        conn = bd.connect()
        cursor = conn.cursor()
        vips = vip_verifie(cursor)
        alerta = None
        if vips > 10:
            print(vips)
            alerta = 'Não é possível adicionar mais de 10 carros como VIP'
        else:
            set_vip(conn, cursor, idcarros)
        cursor.close()
        conn.close()
        return redirect(url_for('available_cars', erro=alerta))
    else:
        return redirect(url_for('home'))


@app.route('/tornar_normal/<idcarros>')
def tornar_normal(idcarros):
    if login_type:
        conn = bd.connect()
        cursor = conn.cursor()
        unset_vip(conn, cursor, idcarros)
        cursor.close()
        conn.close()
        return redirect(url_for('available_cars'))
    else:
        return redirect(url_for('home'))


@app.route('/alterar_preco/<idcarros>', methods=['post'])
def alterar_preco(idcarros):
    preco = request.form.get('preco')
    if login_type:
        conn = bd.connect()
        cursor = conn.cursor()
        update_preco(conn, cursor, idcarros, preco)
        cursor.close()
        conn.close()
        return redirect(url_for('available_cars'))
    else:
        return redirect(url_for('home'))


@app.route('/alterar_usuario')
def usuarios():
    if login_type == 1:
        conn = bd.connect()
        cursor = conn.cursor()
        users = show_users(cursor)
        cursor.close()
        conn.close()
        return render_template('alterar_user.html', logado=login_type, users=users)
    else:
        return redirect(url_for('home'))


@app.route('/tornar_gerente/<iduser>')
def set_gerente(iduser):
    if login_type == 1:
        conn = bd.connect()
        cursor = conn.cursor()
        tornar_gerente(conn, cursor, iduser)
        cursor.close()
        conn.close()
        return redirect(url_for('usuarios'))
    else:
        return redirect(url_for('home'))


@app.route('/tornar_vendedor/<iduser>')
def set_vendedor(iduser):
    if login_type == 1:
        conn = bd.connect()
        cursor = conn.cursor()
        tornar_vendedor(conn, cursor, iduser)
        cursor.close()
        conn.close()
        return redirect(url_for('usuarios'))
    else:
        return redirect(url_for('home'))



@app.route('/excluir/<iduser>')
def delete_user(iduser):
    if login_type == 1:
        conn = bd.connect()
        cursor = conn.cursor()
        excluir_user(conn, cursor, iduser)
        cursor.close()
        conn.close()
        return redirect(url_for('usuarios'))
    else:
        return redirect(url_for('home'))


@app.route('/all_cars')
def all_cars_available(erro=None):
    conn = bd.connect()
    cursor = conn.cursor()
    cars = show_available_cars_comp(cursor)
    cursor.close()
    conn.close()
    return render_template('carros_disponiveis.html', cars=cars, logado=login_type, erro=erro)


@app.route('/vendidos')
def unavailable_cars():
    if login_type:
        conn = bd.connect()
        cursor = conn.cursor()
        carros = show_unavailable_cars(cursor)
        cursor.close()
        conn.close()
        return render_template('vendidos.html', carros=carros, logado=login_type)
    else:
        return redirect(url_for('home'))


@app.route('/buscar', methods=['get'])
def busca():
    pesquisa = request.args.get('buscar')
    print(pesquisa)
    conn = bd.connect()
    cursor = conn.cursor()
    cars = buscar_carro(cursor, pesquisa)
    cursor.close()
    conn.close()
    return render_template('pesquisa.html', cars=cars, logado=login_type)


@app.route('/reservados')
def all_reserved_cars():
    if login_type:
        conn = bd.connect()
        cursor = conn.cursor()
        reserv = show_reservas(cursor)
        cursor.close()
        conn.close()
        return render_template('reservados.html', reserv=reserv, logado=login_type)
    else:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)