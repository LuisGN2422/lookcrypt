import os
import mysql.connector
from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from cryptography.fernet import Fernet
from datetime import datetime
import time

app = Flask(__name__)

# Generar una clave de encriptación
key = Fernet.generate_key()
fernet = Fernet(key)
cipher_suite = Fernet(key)

# Generar una clave de desencriptación a partir de la clave de encriptación
desencriptar_key = key

# Crear un objeto Fernet para desencriptar archivos
fernet_desencriptar = Fernet(desencriptar_key)

# Configuración de la base de datos
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345",
  database="mydb"
)

mycursor = mydb.cursor()
# Crear tabla para almacenar el historial de archivos
mycursor.execute("CREATE TABLE IF NOT EXISTS historialen (id INT AUTO_INCREMENT PRIMARY KEY, nombre_archivo VARCHAR(255), fecha_hora DATETIME, accion VARCHAR(10))")
mycursor.execute("CREATE TABLE IF NOT EXISTS historialdes (id INT AUTO_INCREMENT PRIMARY KEY, nombre_archivo VARCHAR(255), fecha_hora DATETIME, accion VARCHAR(10))")
#Base de datos de las URLS
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS urls (id INT AUTO_INCREMENT PRIMARY KEY, url_encrypted TEXT, url_decrypted TEXT, date_created DATETIME)")

# Función para validar las credenciales del usuario
def validate_user(email, password):
    mycursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = mycursor.fetchone()
    if user:
        return True
    else:
        return False


@app.route('/encrypt', methods=['POST'])
def encrypt():
    archivo = request.files['archivo']
    nombre_archivo = archivo.filename
    archivo_encriptado = fernet.encrypt(archivo.read())
    with open('archivos_encriptados/' + nombre_archivo + '.enc', 'wb') as f:
        f.write(archivo_encriptado)
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mycursor.execute("INSERT INTO historialEn (nombre_archivo, fecha_hora, accion) VALUES (%s, %s, %s)", (nombre_archivo, fecha_hora, "Encrypt"))
    mydb.commit()
    return redirect('/index2')

@app.route('/decrypt', methods=['POST'])
def decrypt():
    archivo = request.files['archivo']
    nombre_archivo = archivo.filename.split('.enc')[0]
    #archivo.filename es una cadena que contiene el nombre del archivo que en este caso es archivo_encryptado
    #.split('.enc') divide la cadena en dos partes: la parte antes de la cadena ".enc" y la parte después de ella. Si el nombre del archivo no contiene ".enc", .split('.enc') devolverá una lista con solo un elemento que es la cadena original.
    archivo_encriptado = archivo.read()
    archivo_desencriptado = fernet_desencriptar.decrypt(archivo_encriptado)
    with open('archivos_desencriptados/' + nombre_archivo, 'wb') as f:
        f.write(archivo_desencriptado)
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mycursor.execute("INSERT INTO historialdes (nombre_archivo, fecha_hora, accion) VALUES (%s, %s, %s)", (nombre_archivo, fecha_hora, "Decrypt"))
    mydb.commit()
    return redirect('/index2')

# Ruta para cargar la página de inicio de sesión
@app.route('/')
def index():
    return render_template('index.html')


# Ruta para procesar el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    if validate_user(email, password):
        return redirect(url_for('index2'))
    else:
        return "Credenciales inválidas"

# Ruta para cargar la página principal después de iniciar sesión
@app.route('/index2')
def index2():
    return render_template('index2.html')

@app.route('/url')
def url():
    return render_template('url.html')


@app.route("/encrypt2", methods=["POST"])
def encrypt2():
    url = request.form["url"]
    encrypted_url = cipher_suite.encrypt(url.encode("utf-8")).decode("utf-8")
    #Esta línea de código en Python cifra una URL utilizando un algoritmo de cifrado y luego la convierte a una cadena de texto decodificada en formato UTF-8.
    # Guardar información en la base de datos
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO urls (url_encrypted, date_created) VALUES (%s, %s)"
    val = (encrypted_url, date_now)
    mycursor.execute(sql, val)
    mydb.commit()

    return render_template("result.html", result=encrypted_url)


@app.route("/decrypt2", methods=["POST"])
def decrypt2():
    encrypted_url = request.form["encrypted_url"]
    decrypted_url = cipher_suite.decrypt(encrypted_url.encode("utf-8")).decode("utf-8")

    # Guardar información en la base de datos
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO urls (url_decrypted, date_created) VALUES (%s, %s)"
    val = (decrypted_url, date_now)
    mycursor.execute(sql, val)
    mydb.commit()

    return render_template("result.html", result=decrypted_url)



@app.route('/register')
def register():
    return render_template('register.html')

# Ruta para procesar el registro de usuario
@app.route('/register', methods=['POST'])
def register_post():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    # Comprobar si el correo ya existe
    mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = mycursor.fetchone()
    if user:
        return "El correo ya existe"
    else:
        # Insertar el nuevo usuario en la base de datos
        sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        val = (username, password, email)
        mycursor.execute(sql, val)
        mydb.commit()
        return "Cuenta creada con éxito"

#Filtroooos
@app.route('/historial')
def historial():
    mycursor.execute("SELECT * FROM historialEn")
    rows_en = mycursor.fetchall()
    mycursor.execute("SELECT * FROM historialdes")
    rows_des = mycursor.fetchall()
    mycursor.execute("SELECT * FROM urls")
    rows_urls = mycursor.fetchall()
    mycursor.execute("SELECT COUNT(*) FROM historialen WHERE accion = 'Encrypt'")
    num_archivos_encriptados = mycursor.fetchone()
    mycursor.execute("SELECT COUNT(*) FROM historialdes WHERE accion = 'Decrypt'")
    num_desencriptados = mycursor.fetchone()
    mycursor.execute("SELECT COUNT(*) FROM urls WHERE url_encrypted IS NOT NULL")
    num_urls_encriptadas = mycursor.fetchone()
    mycursor.execute("SELECT COUNT(*) FROM urls WHERE url_decrypted IS NOT NULL")
    num_urls_desencriptadas = mycursor.fetchone()
    return render_template('historial.html', rows_en=rows_en, rows_des=rows_des, rows_urls=rows_urls,
                            num_archivos_encriptados=num_archivos_encriptados, num_desencriptados=num_desencriptados,
                           num_urls_encriptadas=num_urls_encriptadas, num_urls_desencriptadas=num_urls_desencriptadas)


@app.route('/result')
def result():
    return render_template('result.html')


if __name__ == '__main__':
    app.run(debug=True)