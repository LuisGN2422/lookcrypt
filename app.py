import os
from flask import Flask, render_template, request, redirect, send_from_directory
from cryptography.fernet import Fernet
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Generar una clave de encriptación
key = Fernet.generate_key()
fernet = Fernet(key)

# Generar una clave de desencriptación a partir de la clave de encriptación
desencriptar_key = key

# Crear un objeto Fernet para desencriptar archivos
fernet_desencriptar = Fernet(desencriptar_key)

# Configurar la conexión a la base de datos MySQL
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

@app.route('/')
def home():
    return render_template('index2.html')

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
    return redirect('/')

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
    return redirect('/')

@app.route('/historial')
def historial():
    mycursor.execute("SELECT * FROM historialEn")
    rows_en = mycursor.fetchall()
    mycursor.execute("SELECT * FROM historialdes")
    rows_des = mycursor.fetchall()
    mycursor.execute("SELECT * FROM urls")
    rows_urls = mycursor.fetchall()
    mycursor.execute("SELECT * FROM users")
    rows_users = mycursor.fetchall()
    return render_template('historial.html', rows_en=rows_en, rows_des=rows_des, rows_urls=rows_urls,
                           rows_users=rows_users)


@app.route('/url')
def url():
    return render_template('url.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)



