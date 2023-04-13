from cryptography.fernet import Fernet
from flask import Flask, request, render_template
from datetime import datetime
import mysql.connector

app = Flask(__name__)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Configuración de la conexión a la base de datos
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="mydb"
)

mycursor = mydb.cursor()

# Crear tabla para almacenar la información
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS urls (id INT AUTO_INCREMENT PRIMARY KEY, url_encrypted TEXT, url_decrypted TEXT, date_created DATETIME)")


@app.route("/")
def url():
   return render_template("url.html")


@app.route("/encrypt", methods=["POST"])
def encrypt():
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


@app.route("/decrypt", methods=["POST"])
def decrypt():
    encrypted_url = request.form["encrypted_url"]
    decrypted_url = cipher_suite.decrypt(encrypted_url.encode("utf-8")).decode("utf-8")

    # Guardar información en la base de datos
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO urls (url_decrypted, date_created) VALUES (%s, %s)"
    val = (decrypted_url, date_now)
    mycursor.execute(sql, val)
    mydb.commit()

    return render_template("result.html", result=decrypted_url)


if __name__ == "__main__":
    app.run(debug=True)

