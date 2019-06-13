def set_car(conn, cursor, marca, modelo, foto, preco, placa, vip):
    cursor.execute(f'insert into carros (marca, modelo, placa, vip, path_ft, preco) values ("{marca}", "{modelo}", "{placa}", "{vip}", "{foto}", "{preco}");')
    conn.commit()


def vip_verifie(cursor):
    cursor.execute(f'select count(*) from carros where vip = 1')
    vips = cursor.fetchone()
    if vips is None:
        vips = 0
    return vips


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
