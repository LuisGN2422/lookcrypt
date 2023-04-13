import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Configuración de la base de datos
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345",
  database="mydb"
)

mycursor = mydb.cursor()

# Función para validar las credenciales del usuario
def validate_user(email, password):
    mycursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = mycursor.fetchone()
    if user:
        return True
    else:
        return False

# Función para validar las credenciales del administrador
def validate_admin(email, password):
    mycursor.execute("SELECT * FROM administrators WHERE email = %s AND password = %s", (email, password))
    admin = mycursor.fetchone()
    if admin:
        return True
    else:
        return False


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
    elif validate_admin(email, password):
        return redirect(url_for('historial'))
    else:
        return "Credenciales inválidas"

# Ruta para cargar la página principal después de iniciar sesión
@app.route('/index2')
def index2():
    return render_template('index2.html')



@app.route('/register')
def register():
    return render_template('register.html')

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


if __name__ == '__main__':
    app.run(debug=True)
