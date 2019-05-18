def set_foto(conn, cursor, foto):
    cursor.execute(f'insert into teste (image) values ("{foto}");')
    conn.commit()


def show_foto(cursor):
    cursor.execute(f'select image from teste')
    fotos = cursor.fetchall()
    return fotos
