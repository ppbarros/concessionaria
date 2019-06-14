def set_car(conn, cursor, marca, modelo, foto, preco, placa, vip):
    cursor.execute(f'insert into carros (marca, modelo, placa, vip, path_ft, preco) values ("{marca}", "{modelo}", "{placa}", "{vip}", "{foto}", "{preco}");')
    conn.commit()


def vip_verifie(cursor):
    cursor.execute(f'select count(*) from carros where vip = 1 and idcomp is NULL')
    vips = cursor.fetchone()
    if vips is None:
        vips = 0
    return vips[0]


def show_vips(cursor):
    cursor.execute(f'select idcarros, marca, modelo, path_ft, preco from carros where vip = 1 and idcomp is NULL')
    vips = cursor.fetchall()
    return vips


def validate_login(cursor, user, passwd):
    cursor.execute(f'select tipo, nome from usuarios where login = "{user}" and senha = "{passwd}";')
    usuario = cursor.fetchone()
    if usuario:
        tipo = usuario[0]
        nome = usuario[1]
        return tipo, nome
    else:
        return None


def reservar_carro(conn, cursor, nome, cpf, tel, idcarros):
    cursor.execute(f'select idcomp from comp where cpf = "{cpf}";')
    existe = cursor.fetchone()
    if existe is None:
        cursor.execute(f'insert into comp (nome, cpf, tel) values ("{nome}", "{cpf}", "{tel}");')
        conn.commit()
    cursor.execute(f'select idcomp from comp where cpf = "{cpf}";')
    idcomp = cursor.fetchone()[0]
    cursor.execute(f'update carros set idcomp = {idcomp} where idcarros = {idcarros}')
    conn.commit()


def show_all_cars(cursor):
    cursor.execute(f'select * from carros')
    carros = cursor.fetchall()
    return carros


def show_available_cars(cursor):
    cursor.execute(f'select * from carros where vendido = 0')
    carros = cursor.fetchall()
    return carros


def show_unavailable_cars(cursor):
    cursor.execute(f'select * from carros where vendido = 1')
    carros = cursor.fetchall()
    return carros


def create_first_user(conn, cursor):
    cursor.execute(f'select count(*) from usuarios')
    qnt = cursor.fetchone()
    if qnt is None:
        qnt = 0
    if qnt == 0:
        cursor.execute(f'insert into usuarios (login, senha, tipo, nome) values ("admin", "admin", 1, "admin")')
        conn.commit()


def create_user(conn, cursor, user, passwd, tipo, nome):
    cursor.execute(f'insert into usuarios (login, senha, tipo, nome) values ("{user}", "{passwd}", {tipo}, "{nome}")')
    conn.commit()


def limpar_reserva(conn, cursor, idcarros):
    cursor.execute(f'update carros set idcomp = NULL where idcarros = {idcarros}')
    conn.commit()


def set_vip(conn, cursor, idcarros):
    cursor.execute(f'update carros set vip = 1 where idcarros = {idcarros}')
    conn.commit()


def unset_vip(conn, cursor, idcarros):
    cursor.execute(f'update carros set vip = 0 where idcarros = {idcarros}')
    conn.commit()


def update_preco(conn, cursor, idcarros, preco):
    cursor.execute(f'update carros set preco = {preco} where idcarros = {idcarros}')
    conn.commit()


def show_users(cursor):
    cursor.execute('select * from usuarios')
    users = cursor.fetchall()
    return users


def tornar_gerente(conn, cursor, iduser):
    cursor.execute(f'update usuarios tipo = 1 where idusuarios = {iduser}')
    conn.commit()


def tornar_vendedor(conn, cursor, iduser):
    cursor.execute(f'update usuarios tipo = 0 where idusuarios = {iduser}')
    conn.commit()


def excluir_user(conn, cursor, iduser):
    cursor.execute(f'delete from usuarios where idusuarios = {iduser}')
    conn.commit()


def show_available_cars_comp(cursor):
    cursor.execute(f'select * from carros where vendido = 0 and idcom is NULL')
    carros = cursor.fetchall()
    return carros


def buscar_carro(cursor, buscar):
    cursor.execute(f'select * from carros where nome = "{buscar}" or marca = "{buscar}"')
    pesquisa = cursor.fetchall()
    return pesquisa