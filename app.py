import pymysql
import requests
import json
from flask import jsonify
from flask import flash, request
from flask import Flask
from config import get_db
import sqlite3

app = Flask(__name__)

@app.route('/')
def ping():
    return "hola mundo"

def connect_to_db():
    conn = sqlite3.connect('condominio-1.db')
    return conn


########################################### ZONA DE METODOS #######################################

######################### Listar todo ##################################


#usuarios
@app.route('/usuario')
def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id_usuario, rut, nombre, apellido, email, nro_depto FROM usuario JOIN departamento d on d.fk_id_usuario = id_usuario;")
        rows = cur.fetchall()
        for i in rows:
            user = {}
            user["id_usuario"] = i["id_usuario"]
            user["rut"] = i["rut"]
            user["nombre"] = i["nombre"]
            user["apellido"] = i["apellido"]
            user["email"] = i["email"]
            user["nro_depto"] = i["nro_depto"]
            users.append(user)
    except:
        users = []

    return users

#deptos
@app.route('/departamento')
def get_depts():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id_departamento, nro_depto, us.nombre || ' ' || us.apellido 'nombre', us.rut 'rut', us.email 'email' \
                    from departamento join usuario us on fk_id_usuario = us.id_usuario;")
        rows = cur.fetchall()
        for i in rows:
            user = {}
            user["id_departamento"] = i["id_departamento"]
            user["nro_depto"] = i["nro_depto"]
            user["nombre"] = i["nombre"]
            user["rut"] = i["rut"]
            user["email"] = i["email"]
            users.append(user)
    except:
        users = []

    return users

#reservas anuladas
@app.route('/anulados')
def get_anulados():
    dep = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("Select EMP_ID 'emp_id', ENTRY_DATE 'entry_date', FECHA 'fecha', hora_inicio, hora_termino, id_departamento FROM anulados;")
        rows = cur.fetchall()
        for i in rows:
            deps = {}
            deps["emp_id"] = i["EMP_ID"]
            deps["entry_date"] = i["entry_date"]
            deps["fecha"] = i["fecha"]
            deps["hora_inicio"] = i["hora_inicio"]
            deps["hora_termino"] = i["hora_termino"]
            deps["id_departamento"] = i["id_departamento"]
            dep.append(deps)
    except Exception as e:
        print(e)

    return dep


################################# Traer por id #########################


#Usuario por id
@app.route('/usuario/<int:id_usuario>')
def get_user_by_id(id_usuario):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id_usuario, rut, nombre, apellido, email, nro_depto FROM usuario JOIN departamento d on d.fk_id_usuario = id_usuario WHERE id_usuario = ?", (id_usuario,))
        row = cur.fetchone()
        if row is not None:
            user["id_usuario"] = row["id_usuario"]
            user["rut"] = row["rut"]
            user["nombre"] = row["nombre"]
            user["apellido"] = row["apellido"]
            user["email"] = row["email"]
            user["nro_depto"] = row["nro_depto"]
    except:
        pass
    return user



################################# Crear ################################


#Crear usuario
@app.route('/create/usuario', methods=['POST'])
def create_user():
    try:
        if request.method == 'POST':
            rut = request.form['rut']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            email = request.form['email']
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO usuario(rut,nombre,apellido,email) VALUES (?,?,?,?)",(rut, nombre, apellido, email))
            conn.commit()
            inserted_user = get_user_by_id(cur.lastrowid)
            msg = "success!"
    except:
        conn().rollback()
        msg = "Something went wrong"
    finally:
        conn.close()
        return msg



#crear reserva
@app.route('/create/reserva', methods=['POST'])
def create_resv():
    try:
        if request.method == 'POST':
            fecha = request.form['fecha']
            hora_inicio = request.form['hora_inicio']
            hora_termino = request.form['hora_termino']
            espacio_comun = request.form['espacio_comun']
            id_departamento = request.form['id_departamento']
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO reserva_ec(fecha,hora_inicio,hora_termino,estado,fk_id_ec,fk_id_departamento) VALUES (?,?,?,0,?,?)",(fecha, hora_inicio, hora_termino, espacio_comun, id_departamento))
            conn.commit()
            inserted_user = get_user_by_id(cur.lastrowid)
            msg = "Success!"
    except:
        conn().rollback()
        msg = "Something went wrong"
    finally:
        conn.close()
        return msg



################################ Eliminar ##############################
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_emp(id):
	try:
		conn = connect_to_db()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM reserva_ec WHERE id_reserva_ec = ?", (id,))
		conn.commit()
		respone = jsonify('Reserva eliminada!')
		respone.status_code = 200
		return respone
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

################################ Actualiza #############################

################## Levantar servidor ####################
if __name__ == '__main__':                             ##
    app.run(debug=True, port=5000)                     ##
#########################################################
