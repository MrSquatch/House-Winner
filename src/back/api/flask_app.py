from datetime import datetime
import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS # Agregar CORS
from flask_mysqldb import MySQL
import pandas as pd
import config

app = Flask(__name__)

# Configuración de la conexión a la base de datos
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

# Habilitar CORS para todas las rutas
CORS(app)

# ============================================================
# Rutas

file_path = os.path.dirname(__file__)
data_path = '../database/data/'

# RUTAS LOGIN
# Ruta para cargar datos desde el archivo CSV a la base de datos
@app.route('/api/insertar/alumnos', methods=['GET'])
def insertar_alumnos():
    try:
        csv_path = os.path.join(file_path, data_path, 'alumnos.csv')

        # Cargar el archivo CSV en un DataFrame de Pandas
        df = pd.read_csv(csv_path, delimiter='\t', encoding='utf-8')

        # Conexión al cursor de la base de datos
        cur = mysql.connection.cursor()

        # Iterar sobre cada fila del DataFrame e insertar en la base de datos
        for index, row in df.iterrows():
            # Obtener los valores de cada columna
            cod_alumno = row['cod_alumno']
            nombres = row['nombres']
            apellidos = row['apellidos']
            escuela_prof = row['escuela_prof']

            # Ejecutar la consulta SQL para insertar en la tabla alumnos
            cur.execute("INSERT INTO alumnos (cod_alumno, nombres, apellidos, escuela_prof) VALUES (%s, %s, %s, %s)",
                        (cod_alumno, nombres, apellidos, escuela_prof))

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar cursor
        cur.close()

        return 'ALUMNOS cargados correctamente en la base de datos.'

    except Exception as e:
        return f'Error al cargar los datos de ALUMNOS: {str(e)}'

# Ruta para cargar datos de administradores desde el archivo CSV a la base de datos
@app.route('/api/insertar/admins', methods=['GET'])
def insertar_admins():
    try:
        csv_path = os.path.join(file_path, data_path, 'administradores.csv')

        # Cargar el archivo CSV en un DataFrame de Pandas
        df = pd.read_csv(csv_path, delimiter='\t', encoding='utf-8')

        # Conexión al cursor de la base de datos
        cur = mysql.connection.cursor()

        # Iterar sobre cada fila del DataFrame e insertar en la base de datos
        for index, row in df.iterrows():
            # Obtener los valores de cada columna
            cod_admin = row['cod_admin']
            nombres = row['nombres']
            apellidos = row['apellidos']
            cargo = row['cargo']

            # Ejecutar la consulta SQL para insertar en la tabla administradores
            cur.execute("INSERT INTO administradores (cod_admin, nombres, apellidos, cargo) VALUES (%s, %s, %s, %s)",
                        (cod_admin, nombres, apellidos, cargo))

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar cursor
        cur.close()

        return 'ADMINISTRADORES cargados correctamente en la base de datos.'

    except Exception as e:
        return f'Error al cargar los datos de ADMINISTRADORES: {str(e)}'

# Ruta para insertar usuarios
@app.route('/api/insertar/usuarios', methods=['GET'])
def insertar_usuarios():
    try:
        csv_path = os.path.join(file_path, data_path, 'usuarios.csv')

        # Cargar el archivo CSV en un DataFrame de Pandas
        df = pd.read_csv(csv_path, delimiter='\t', encoding='utf-8')

        # Conexión al cursor de la base de datos
        cur = mysql.connection.cursor()

        # Iterar sobre cada fila del DataFrame e insertar en la base de datos
        for index, row in df.iterrows():
            # Obtener los valores de cada columna para usuarios/administradores
            id_usuario = row['id_usuario']
            cod_admin = row['cod_admin']
            cod_alumno = row['cod_alumno']
            username = row['username']
            password = row['password']
            rol = row['rol']

            # Verificar si es un administrador o un usuario
            if pd.notna(cod_admin):
                # Es un administrador
                cur.execute("INSERT INTO usuarios_sist (id_usuario, cod_admin, username, password, rol) "
                            "VALUES (%s, %s, %s, %s, %s)",
                            (id_usuario, cod_admin, username, password, rol))
            elif pd.notna(cod_alumno):
                # Es un alumno
                cur.execute("INSERT INTO usuarios_sist (id_usuario, cod_alumno, username, password, rol) "
                            "VALUES (%s, %s, %s, %s, %s)",
                            (id_usuario, cod_alumno, username, password, rol))

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar cursor
        cur.close()

        return 'Datos de USUARIOS cargados correctamente en la base de datos.'

    except Exception as e:
        return f'Error al cargar los datos de USUARIOS: {str(e)}'

# Ruta para autenticación de usuarios
@app.route('/api/login', methods=['POST'])
def login():
    # Obtener datos del formulario
    username = request.json.get('username')
    password = request.json.get('password')

    # Validar que se recibieron el usuario y contraseña
    if not username or not password:
        return jsonify({'message': 'Se requiere usuario y contraseña'}), 400

    # Conexión al cursor de la base de datos
    cur = mysql.connection.cursor()

    try:
        # Consultar si el usuario existe en la base de datos
        cur.execute("SELECT id_usuario, cod_admin, cod_alumno, username, password, rol FROM usuarios_sist WHERE username = %s", (username,))
        usuario = cur.fetchone()

        if not usuario:
            return jsonify({'message': 'Credenciales incorrectas'}), 401

        # Verificar la contraseña
        stored_password = usuario[4]
        if password == stored_password:
            # Contraseña válida, determinar tipo de usuario
            return jsonify({
                'message': 'Autenticación exitosa',
                'username': usuario[3],
                'rol': usuario[5]
            }), 200
        else:
            # Contraseña incorrecta
            return jsonify({'message': 'Credenciales incorrectas'}), 401

    except Exception as e:
        return jsonify({'message': f'Error en la autenticación: {str(e)}'}), 500

    finally:
        # Cerrar cursor
        cur.close()

# RUTAS LIBROS
# Ruta para cargar datos desde el archivo CSV a la tabla libros
@app.route('/api/insertar/libros', methods=['GET'])
def insertar_libros():
    try:
        csv_path = os.path.join(file_path, data_path, 'libros.csv')

        # Cargar el archivo CSV en un DataFrame de Pandas
        df = pd.read_csv(csv_path, delimiter='\t', encoding='latin-1')

        # Conexión al cursor de la base de datos
        cur = mysql.connection.cursor()

        # Iterar sobre cada fila del DataFrame e insertar en la tabla libros
        for index, row in df.iterrows():
            # Obtener los valores de cada columna
            id_libro = row['id_libro']
            isbn = row['isbn']
            titulo = row['titulo']
            descrip = row['descrip'] if pd.notna(row['descrip']) else None
            autor = row['autor']
            editorial = row['editorial']
            anio_publicacion = row['anio_publicacion']
            estado = row['estado']

            # Ejecutar la consulta SQL para insertar en la tabla libros
            cur.execute("""
                INSERT INTO libros (id_libro, isbn, titulo, descrip, autor, editorial, anio_publicacion, estado) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_libro, isbn, titulo, descrip, autor, editorial, anio_publicacion, estado))

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar cursor
        cur.close()

        return 'LIBROS cargados correctamente en la base de datos.'

    except Exception as e:
        return f'Error al cargar los datos de LIBROS: {str(e)}'

# Ruta para devolver libros dado un termino de busqueda
@app.route('/api/buscarLibro', methods=['POST'])
def buscar_libro():
    try:
        # Obtener el JSON del cuerpo de la solicitud
        data = request.get_json()

        # Lista de campos permitidos
        campos_permitidos = ['titulo', 'isbn']

        # Filtrar los campos presentes en el JSON que están en la lista de campos permitidos
        campos_presentes = [campo for campo in data if campo in campos_permitidos]

        # Validar que haya exactamente un campo permitido y que sea una cadena válida
        if len(campos_presentes) != 1:
            abort(400, f'El JSON debe contener exactamente uno de los siguientes campos: {", ".join(campo for campo in campos_permitidos)}')

        campo = campos_presentes[0]
        if not isinstance(data[campo], str):
            abort(400, f'El campo "{campo}" debe ser una cadena válida')

        # Realizar query dependiendo del campo presente
        termino = data[campo]
        cur = mysql.connection.cursor()

        if(campo == 'isbn'):
            if not termino:
                abort('El campo "isbn" no puede estar vacío')
            
            query = f"SELECT * FROM libros WHERE isbn = {termino}"
            cur.execute(query)
        else:
            query = f"SELECT * FROM libros WHERE {campo} LIKE %s"
            cur.execute(query, ('%' + termino + '%',))

        # Obtener los resultados de la consulta
        resultados = cur.fetchall()

        # Cerrar cursor
        cur.close()

        # Si no se encontraron resultados, retornar un mensaje adecuado
        if not resultados:
            return jsonify({'mensaje': f'No se encontraron libros que coincidan con el {campo}: "{termino}"'}), 404

        # Convertir resultados a una lista de diccionarios
        libros = []
        for libro in resultados:
            pathPortada = f"/backend/database/data/libros_portadas/{libro[0]}.jpg"
            descrip = libro[3] if libro[3]!=None else ''

            libro_dict = {
                'id_libro': libro[0],
                'isbn': libro[1],
                'titulo': libro[2],
                'descrip': descrip,
                'autor':libro[4],
                'editorial': libro[5],
                'anio_publicacion': libro[6],
                'estado': libro[7],
                'pathPortada' : pathPortada
            }
            libros.append(libro_dict)

        # Contar la cantidad de libros encontrados
        cantidad_libros = len(libros)

        # Verifica si no hay mas de un libro con el mismo isbn
        if(campo == 'isbn' and cantidad_libros>1):
            return jsonify({'Error': f'Mas de un libro coincide con el isbn "{termino}"'}), 404
        
        # Devolver los resultados en formato JSON incluyendo la cantidad de libros
        return jsonify({'cantidad_libros': cantidad_libros, 'libros': libros})

    except Exception as e:
        return f'Error al buscar libros: {str(e)}', 500

# Ruta para devolver libros dado un termino de busqueda
@app.route('/api/editarCatalogo', methods=['POST'])
def editar_catalogo():
    try:
        # Obtener el JSON del cuerpo de la solicitud
        input = request.get_json()

        if not (len(input) == 2 and 'tipo' in input and 'columnas' in input):
            abort(400, f'El JSON debe tener "tipo" y "columnas"')

        tipo = input['tipo']
        columnas = input['columnas']

        if tipo not in ['update','create']:
            abort(400, f'El objeto "tipo" del JSON solo puede ser "create" o "update"')

        campos_necesarios = ['titulo','descrip','autor','anio','editorial','isbn','estado']
        campos_filtrados = [campo for campo in columnas if campo in campos_necesarios]
        
        if len(campos_filtrados) != len(campos_necesarios):
            abort(400, f'El objeto "data" del JSON debe tener todos los campos')
        
        cur = mysql.connection.cursor() 

        # Acceder a los valores en el diccionario columnas
        titulo = columnas['titulo']
        descrip = columnas['descrip']
        autor = columnas['autor']
        anio = int(columnas['anio'])
        editorial = columnas['editorial']
        isbn = columnas['isbn']
        estado = columnas['estado']  

        if (tipo == 'update'):
            query = '''
            UPDATE libros
            SET
                titulo = %s,
                descrip = %s,
                autor = %s,
                editorial = %s,
                anio_publicacion = %s,                
                estado = %s
            WHERE isbn = %s
            '''
            valores_query = [titulo,descrip,autor,editorial,anio,estado,isbn]
        
        elif(tipo == 'create'):
            query = '''
            INSERT INTO libros (isbn, titulo, descrip, autor, editorial, anio_publicacion, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            valores_query = [isbn, titulo, descrip, autor, editorial, anio, estado]

        cur.execute(query, valores_query)
        mysql.connection.commit()

        # Verificar si se realizaron cambios
        if cur.rowcount == 0:
            return jsonify({'message':f'El pedido realizado no ha modificado ninguna fila.'}),400

        # Obtener el ID del nuevo libro insertado
        if(tipo=='create'):        
            libro_id = cur.lastrowid

        cur.close()

        if(tipo == 'update'):
            return jsonify({'message':f'Libro actualizado correctamente con ISBN: {isbn}'}), 200

        if(tipo == 'create'):
            return jsonify({'message':f'Libro creado correctamente con ID "{libro_id}" e ISBN "{isbn}"'}), 200

    except Exception as e:
        return f'Error al editar el catalogo: {str(e)}', 500

# Ruta para devolver libros dado un termino de busqueda
@app.route('/api/eliminarLibro', methods=['POST'])
def eliminar_libro():
    try:
        # Obtener el JSON del cuerpo de la solicitud
        input = request.get_json()

        if not (len(input) == 1 and 'isbn' in input):
            abort(400, f'El JSON debe tener solo el campo "isbn"')

        isbn = input['isbn']
        
        cur = mysql.connection.cursor() 

        query = f'delete from libros where isbn = "{isbn}"'

        cur.execute(query)
        mysql.connection.commit()

        # Verificar si se realizaron cambios
        if cur.rowcount == 0:
            return jsonify({'message':f'El pedido realizado no ha modificado ninguna fila. Verifique el ISBN ingresado'}),400

        cur.close()
        return jsonify({'message':f'Libro eliminado correctamente con ISBN: {isbn}'}), 200
        

    except Exception as e:
        return f'Error al intentar realizar la eliminacion del libro: {str(e)}', 500

# RUTAS PUPITRES
# Ruta para cargar datos desde el archivo CSV a la tabla pupitres
@app.route('/api/insertar/pupitres', methods=['GET'])
def insertar_pupitres():
    try:
        csv_path = os.path.join(file_path, data_path, 'pupitres.csv')

        # Cargar el archivo CSV en un DataFrame de Pandas
        df = pd.read_csv(csv_path, delimiter='\t', encoding='utf-8')

        # Conexión al cursor de la base de datos
        cur = mysql.connection.cursor()

        # Iterar sobre cada fila del DataFrame e insertar en la tabla libros
        for index, row in df.iterrows():
            id_pupitre=int(row['id_pupitre'])
            ubicacion=row['ubicacion']
            estado=row['estado']

            # Ejecutar la consulta SQL para insertar en la tabla libros
            cur.execute("""
                INSERT INTO pupitres (id_pupitre, ubicacion, estado) 
                VALUES (%s, %s, %s)
            """, (id_pupitre, ubicacion, estado))

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar cursor
        cur.close()

        return 'PUPITRES cargados correctamente en la base de datos.'

    except Exception as e:
        return f'Error al cargar los datos de PUPITRES: {str(e)}'
    
# Ruta para cargar datos desde el archivo CSV a la tabla solicitudes
@app.route('/api/insertar/solicitudes', methods=['GET'])
def insertar_solicitudes():
    try:
        csv_path = os.path.join(file_path, data_path, 'solicitudes.csv')

        # Cargar el archivo CSV en un DataFrame de Pandas
        df = pd.read_csv(csv_path, delimiter='\t', encoding='utf-8')

        # Conexión al cursor de la base de datos
        cur = mysql.connection.cursor()

        # Iterar sobre cada fila del DataFrame e insertar en la tabla libros
        for index, row in df.iterrows():
            id_solicitud=row['id_solicitud']
            cod_alumno=row['cod_alumno']
            tipo_solic=row['tipo_solic']
            fecha_solicitud=row['fecha_solicitud']
            justif_solic=row['justif_solic'] if pd.notna(row['justif_solic']) else None
            estado_solic=row['estado_solic']
            admin_encargado=row['admin_encargado']
            observ_solic=row['observ_solic'] if pd.notna(row['observ_solic']) else None

            # Ejecutar la consulta SQL para insertar en la tabla libros
            cur.execute("""
                INSERT INTO solicitudes 
                        (id_solicitud, cod_alumno, tipo_solic, fecha_solicitud, 
                        justif_solic, estado_solic, admin_encargado, observ_solic)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_solicitud, cod_alumno, tipo_solic, fecha_solicitud, 
                  justif_solic, estado_solic, admin_encargado, observ_solic))

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar cursor
        cur.close()

        return 'SOLICITUDES cargados correctamente en la base de datos.'

    except Exception as e:
        return f'Error al cargar los datos de SOLICITUDES: {str(e)}'
    
# Ruta para cargar datos desde el archivo CSV a la tabla pupitre_solicitud
@app.route('/api/insertar/pupitre_solicitud', methods=['GET'])
def insertar_pupitre_solicitud():
    try:
        csv_path = os.path.join(file_path, data_path, 'pupitre_solicitud.csv')

        # Cargar el archivo CSV en un DataFrame de Pandas
        df = pd.read_csv(csv_path, delimiter='\t', encoding='utf-8')

        # Conexión al cursor de la base de datos
        cur = mysql.connection.cursor()

        # Iterar sobre cada fila del DataFrame e insertar en la tabla libros
        for index, row in df.iterrows():
            id_pup_sol=row['id_pup_sol']
            id_solicitud=row['id_solicitud']
            id_pupitre=row['id_pupitre']

            # Ejecutar la consulta SQL para insertar en la tabla libros
            cur.execute("""
                INSERT INTO pupitre_solicitud 
                        (id_pup_sol, id_solicitud, id_pupitre)
                VALUES (%s, %s, %s)
            """, (id_pup_sol, id_solicitud, id_pupitre))

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar cursor
        cur.close()

        return 'PUPITRE_SOLICITUD cargados correctamente en la base de datos.'

    except Exception as e:
        return f'Error al cargar los datos de PUPITRE_SOLICITUD: {str(e)}'

@app.route('/api/obtener_solicitudes/pupitres', methods=['POST'])
def solicitudes_pupitres():
    try:
        # Obtener el JSON del cuerpo de la solicitud
        data = request.get_json()

        # Lista de campos permitidos
        if not (len(data)==1 and 'tipo' in data):
            abort(400, f'El JSON debe contener solamente el campo "tipo"')
        
        valores_aceptados = ['P','C','L']
        if data['tipo'] not in valores_aceptados:
            abort(400, f'El campo "tipo" solo puede ser uno de los'+
                        f'siguientes valores: {", ".join(valores_aceptados)}')

        # Realizar query dependiendo del campo presente
        tipo_solicitud = data['tipo']
        cur = mysql.connection.cursor()

        query = f"""
        SELECT a.cod_alumno,a.nombres,a.apellidos,escuela_prof,justif_solic,
                cod_admin,adm.nombres,adm.apellidos,adm.cargo,observ_solic,
                p.id_pupitre,ubicacion,estado,
                fecha_solicitud,estado_solic
        FROM 
            pupitre_solicitud AS ps
        JOIN 
            solicitudes AS s ON ps.id_solicitud = s.id_solicitud
        JOIN 
            pupitres AS p ON ps.id_pupitre = p.id_pupitre
        JOIN 
            alumnos AS a ON a.cod_alumno = s.cod_alumno
        JOIN 
            administradores AS adm ON adm.cod_admin = s.admin_encargado
        WHERE 
            s.tipo_solic = '{tipo_solicitud}';
        """
        cur.execute(query)

        # Obtener los resultados de la consulta
        resultados = cur.fetchall()

        print(resultados)

        # Cerrar cursor
        cur.close()

        # Si no se encontraron resultados, retornar un mensaje adecuado
        if not resultados:
            return jsonify({'mensaje': f'No se encontraron solicitudes que'+
                            f'coincidan con el tipo de solicitud: "{tipo_solicitud}"'}), 404

        # Convertir resultados a una lista de diccionarios
        solicitudes = []
        for solicitud in resultados:
            admin_observ = solicitud[9] if pd.notna(solicitud[9]) else 'No hay observaciones aún'

            # Reformatea la fecha al formato deseado
            fecha_dt = solicitud[13]
            fecha_formateada = fecha_dt.strftime('%d-%m-%Y')           

            solicitud_dict = {
                'alumno':{
                    'cod_alumno':solicitud[0],
                    'nombres':solicitud[1],
                    'apellidos':solicitud[2],
                    'escuela_prof':solicitud[3],
                    'justif_solic':solicitud[4],
                },
                'admin':{
                    'cod_admin':solicitud[5],
                    'nombres':solicitud[6],
                    'apellidos':solicitud[7],
                    'cargo':solicitud[8],
                    'observ_solic':admin_observ,
                },
                'pupitre':{
                    'id_pupitre':solicitud[10],
                    'ubicacion':solicitud[11],
                    'estado':solicitud[12],

                },
                'fecha_solicitud':fecha_formateada,
                'estado_solic':solicitud[14],
            }
            solicitudes.append(solicitud_dict)

        # Contar la cantidad de solicitudes encontradas
        cantidad_solicitudes = len(solicitudes)

        # Devolver los resultados en formato JSON incluyendo la cantidad de libros
        return jsonify({'cantidad_solicitudes': cantidad_solicitudes, 'solicitudes': solicitudes})

    except Exception as e:
        return f'Error al recuperar las solicitudes: {str(e)}', 500

# ============================================================

# Run app
if __name__ == '__main__':
    app.run(debug=True)
