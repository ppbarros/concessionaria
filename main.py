from flask import Flask, render_template, request, url_for, redirect
from flaskext.mysql import MySQL
from bd import *

app = Flask(__name__)
bd = MySQL()
bd.init_app(app)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'concessionaria'

@app.route('/')
def inicio():
    return render_template('home.html')


@app.route('/inserir', methods=['post'])
def inserir():
    conn = bd.connect()
    cursor = conn.cursor()
    foto = request.files['foto']
    set_foto(conn, cursor, foto)
    cursor.close()
    conn.close()
    return redirect(url_for('inicio'))

@app.route('/fotos')
def fotos():
    conn = bd.connect()
    cursor = conn.cursor()
    fotos = show_foto(cursor)
    cursor.close()
    conn.close()
    return render_template('fotos.html', fot=fotos)



if __name__ == '__main__':
    app.run(debug=True)