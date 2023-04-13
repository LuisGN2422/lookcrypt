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


# Ruta para cargar la página de registro de usuario
@app.route('/')
def register():
    return render_template('register.html')


# Ruta para procesar el registro de usuario
@app.route('/register', methods=['POST'])
def register_post():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    # Verificar si el correo ya existe en la tabla "administrators"
    mycursor.execute("SELECT * FROM administrators WHERE email = %s", (email,))
    admin = mycursor.fetchone()

    if admin:
        return "El correo ya existe"
    else:
        # Verificar si la tabla "administrators" está vacía y agregar un administrador único si es así
        mycursor.execute("SELECT COUNT(*) FROM administrators")
        count = mycursor.fetchone()[0]

        if count == 0:
            sql = "INSERT INTO administrators (username, password, email) VALUES (%s, %s, %s)"
            val = (username, password, email)
            mycursor.execute(sql, val)
            mydb.commit()
            return "Cuenta de administrador creada con éxito"
        else:
            # Insertar el nuevo usuario en la tabla "users"
            sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
            val = (username, password, email)
            mycursor.execute(sql, val)
            mydb.commit()
            return "Cuenta de usuario creada con éxito"


if __name__ == '__main__':
    app.run(debug=True)
