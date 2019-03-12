import sqlite3
from functools import lru_cache
# from cachetools import cached, hashkey

def init():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    return conn, c

# @cached(cache={}, key=lambda db_handle, query: hashkey(query))
@lru_cache(maxsize=32)
def get_cursuri(id_curs=""):
    conn, c = init()
    if id_curs == "":  # get courses collection
        c.execute('SELECT * FROM Cursuri')
        ret = c.fetchall()
    else:
        c.execute('SELECT * FROM Cursuri WHERE Cursuri.id_curs=?', (id_curs,))
        ret = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return ret

@lru_cache(maxsize=32)
def get_studenti(id_student=""):
    conn, c = init()
    if id_student == "":  # get studenti collection
        c.execute('SELECT * FROM Studenti')
        ret = c.fetchall()
    else:
        c.execute('SELECT * FROM Studenti WHERE Studenti.id_student=?', (id_student,))
        ret = c.fetchall()
    c.close()
    conn.close()
    return ret

@lru_cache(maxsize=32)
def get_note(id_nota=""):
    conn, c = init()
    if id_nota == "":  # get note collection
        c.execute('SELECT * FROM Note')
        ret = c.fetchall()
    else:
        c.execute('SELECT * FROM Note WHERE Note.id_nota=?', (id_nota,))
        ret = c.fetchall()
    c.close()
    conn.close()
    return ret


def insert_into_cursuri(values=""):
    """
    :param values:
    id DB_AUTO
    nume mandatory
    credite mandatory

    :return:
    inserted_id - if all good
    error_name - else
    """
    conn, c = init()
    try:
        c.execute('''INSERT INTO Cursuri (nume, credite) VALUES(?,?)''', (str(values['nume']), int(values['credite'])))
        inserted_id = c.lastrowid
        conn.commit()
        c.close()
        conn.close()
        get_cursuri.cache_clear()
        return inserted_id
    except sqlite3.IntegrityError as e:
        conn.rollback()  # ?
        c.close()
        conn.close()
        return str(e)


def insert_into_studenti(values=""):
    pass


def insert_into_note(values=""):
    pass


def put_cursuri(id_curs, modifications):
    '''
    :param id_curs:
    :param modifications:
    :return:
    int done    = 1 (all good)
    str error: message
    '''
    conn, c = init()
    done = 0

    if "id_curs" in modifications.keys() and "nume" in modifications.keys() and "credite" in modifications.keys():
        try:
            sql = """UPDATE Cursuri SET nume=?, credite=? WHERE id_curs = ?"""
            c.execute(sql, (modifications['nume'], int(modifications['credite']), int(modifications["id_curs"])))
            conn.commit()
            c.close()
            conn.close()
            done = c.rowcount
            get_cursuri.cache_clear()
            return done
        except sqlite3.Error as e:
            conn.rollback()
            c.close()
            conn.close()
            return str(e)
    else:
        c.close()
        conn.close()
        return "not all parameters given for valid PUT"


def patch_cursuri(id_curs, modifications):
    '''
    :param id_curs:
    :param modifications:
    :return:
    done: int   = 1 (all good)
                = 0 (not found)
    error: str      message
    '''
    conn, c = init()
    done = 0
    if "nume" in modifications.keys() and "credite" in modifications.keys():
        try:
            sql = """UPDATE Cursuri SET nume=?, credite=? WHERE id_curs = ?"""
            c.execute(sql, (modifications['nume'], int(modifications['credite']), id_curs))
            conn.commit()
            c.close()
            conn.close()
            done = c.rowcount
            get_cursuri.cache_clear()
            return done
        except sqlite3.Error as e:
            c.rollback()
            c.close()
            conn.close()
            print(e)
            return str(e)
    elif "credite" in modifications.keys():
        try:
            c.execute('''UPDATE Cursuri SET credite=? WHERE id_curs = ?''', (int(modifications['credite']), id_curs))
            done = c.rowcount
            conn.commit()
            c.close()
            conn.close()
            get_cursuri.cache_clear()
            return done
        except sqlite3.Error as e:
            c.rollback()
            c.close()
            conn.close()
            print(e)
            return str(e)
    elif "nume" in modifications.keys():
        try:
            c.execute('''UPDATE Cursuri SET NUME=? WHERE id_curs = ?''', (str(modifications['nume']), id_curs))
            done = c.rowcount
            conn.commit()
            c.close()
            conn.close()
            get_cursuri.cache_clear()
            return done
        except sqlite3.Error as e:
            conn.rollback()
            c.close()
            conn.close()
            print(e)
            return str(e)
    else:
        return "something bad just happened while trying to patch too many values"


def delete_cursuri(resource_id):
    '''
    :param resource_id:
    :return:
    done: int   -> 1 : successful
                -> 0 : not found
    done: str   -> error message
    '''
    conn, c = init()
    done = 0
    try:
        sql = 'DELETE FROM Cursuri WHERE id_curs=?'
        c.execute(sql, (resource_id,))
        done = c.rowcount
        conn.commit()
        c.close()
        conn.close()
        return done
    except sqlite3.Error as e:
        return str(e)
