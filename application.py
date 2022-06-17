
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask import render_template,url_for,redirect,request,session,flash
import importacio_airbnb
import re
from datetime import datetime

application = Flask(__name__)
application.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
application.config['MYSQL_USER'] = "root"
application.config['MYSQL_PASSWORD'] = "miquel"
application.config['MYSQL_HOST'] = "127.0.0.1"
application.config['MYSQL_DB'] = "justguest"
application.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(application)
bcrypt = Bcrypt(application)







#----------------------------------------------------------------------------------------------------
@application.route("/",methods=['GET', 'POST'])
@application.route("/login",methods=['GET', 'POST'])
def login():
    msg=""
    if 'loggedin' in session:
        return redirect(url_for('inside'))
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        usuario = request.form["username"]
        pas = request.form["password"]
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = %s',[usuario])
        resultado = cursor.fetchone()
        if resultado:
            if bcrypt.check_password_hash(resultado["password"],pas):
                session['loggedin'] = True
                session['id'] = resultado['idusuario']
                session['email'] = resultado['email']
                session['gestoria'] = resultado['nombre_gestoria']
                session['permisos'] = resultado['permisos']
                session['primeruso'] = resultado['primeruso']
                if resultado["permisos"]=="1":
                    return redirect(url_for('administracion'))
                else:
                    return redirect(url_for('inside'))
            else:
                msg = 'Los datos son incorrectos. Por favor, vuelve a intentarlo.'
        else:
            msg = 'Los datos son incorrectos. Por favor, vuelve a intentarlo.'
    return render_template("login.html",msg=msg)

@application.route("/register",methods=['GET', 'POST'])
def register():
    msg=""
    msg1=""
    if 'loggedin' in session:
        return redirect(url_for('inside'))
    if request.method == "POST" and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        password2 = bcrypt.generate_password_hash(password).decode("utf-8")
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s",[email])
        cuenta = cursor.fetchone()
        if cuenta:
            msg = "Este email ya se encuentra en uso. Por favor, elije otro email."
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'El nombre de la gestoria sólo puede contener letras y números!'
        elif not username or not password or not email:
            msg = 'Por favor, rellena el formulario completo.'
        else:
            cursor.execute("""INSERT INTO usuarios (email,password,nombre_gestoria,primeruso,permisos) VALUES (%s,%s,%s,%s,%s)""",(email,password2,username,"1","2"))
            mysql.connection.commit()
            msg1 = "El registro se ha realizado con éxito!"
    elif request.method == "POST":
        msg = "Rellena el formulario, por favor."



    return render_template("register.html",msg=msg,msg1=msg1)


@application.route("/inside",methods=['GET','POST'])
def inside():
    if 'loggedin' in session:

            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM airbnb WHERE idusuario = %s",[session['id']])
            resultado = cur.fetchone()
            if resultado:
                email = resultado["email"]
                password = resultado["password"]
                if request.method=="POST":
                    mail = request.form["usuario"]
                    passs = request.form["password"]
                    lel = mysql.connection.cursor()
                    lel.execute("UPDATE airbnb SET email = %s,password = %s WHERE idusuario = %s",(mail,passs,session["id"]))
                    lel.connection.commit()
                    flash("Los datos han sido actualizados correctamente!","success")
                    return redirect(url_for('inside'))
                else:
                    flash("Ya tenemos registrados tus datos de Airbnb! Si los introduces de nuevo, se modificaran.","info")
                    return render_template("inside.html",email = email,password=password)
            elif request.method == "POST" and 'usuario' in request.form and 'password' in request.form:
                usuario = request.form['usuario']
                password = request.form['password']
                if not usuario or not password:
                    flash("Por favor, rellena el formulario con los datos.","error")
                else:
                    cursor = mysql.connection.cursor()
                    cursor.execute("""INSERT INTO airbnb (email,password,idusuario) VALUES (%s,%s,%s)""",(usuario,password,session['id']))
                    mysql.connection.commit()
                    flash("Los datos se han enviado correctamente. En breves, los procesaremos!","success")
                return redirect(url_for('inside'))
            else:
                return render_template("inside.html")

    return redirect(url_for("login"))
"""
@application.route("/sincairbnb",methods=['POST','GET'])
def sincairbnb():
    if 'loggedin' in session:

            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM airbnb WHERE idusuario = %s",[session['id']])
            resultado = cur.fetchone()
            if resultado:
                email = resultado["email"]
                password = resultado["password"]
                if request.method=="POST":
                    mail = request.form["usuario"]
                    passs = request.form["password"]
                    lel = mysql.connection.cursor()
                    lel.execute("UPDATE airbnb SET email = %s,password = %s WHERE idusuario = %s",(mail,passs,session["id"]))
                    lel.connection.commit()
                    flash("Los datos han sido actualizados correctamente!","success")
                    return render_template("sincairbnb.html")
                else:
                    flash("Ya tenemos registrados tus datos de Airbnb! Si los introduces de nuevo, se modificaran.","info")
                    return render_template("sincairbnb.html",email = email,password=password)
            elif request.method == "POST" and 'usuario' in request.form and 'password' in request.form:
                msg=""
                usuario = request.form['usuario']
                password = request.form['password']
                if not usuario or not password:
                    flash("Por favor, rellena el formulario con los datos.","error")
                else:
                    cursor = mysql.connection.cursor()
                    cursor.execute("INSERT INTO airbnb (email,password,idusuario) VALUES (%s,%s,%s)",(usuario,password,session['id']))
                    mysql.connection.commit()
                    flash("Los datos se han enviado correctamente. En breves, los procesaremos!","success")
                return render_template("sincairbnb.html")
            else:
                return render_template("sincairbnb.html")

    return redirect(url_for("login"))
"""

@application.route("/anyadirpropiedad",methods=["POST","GET"])
def anyadirpropiedad():
    if 'loggedin' in session:
        if session['permisos'] == "1":
            nom = session["gestoria"]
            cursor = mysql.connection.cursor()

            if request.method == "POST":
                nombre = request.form['nombre']
                direccion = request.form['direccion']
                n_matrimonio = request.form['n_camas_matrimonio']
                n_individuales = request.form['n_camas_individuales']
                n_banyos = request.form['n_banyos']
                capacidad_guests = request.form['capacidad_guests']
                idusuario = request.form['idusuario']
                idairbnb = request.form['idairbnb']
                idbooking = request.form['idbooking']
                checking_time = request.form['checkin_time']
                checkout_time = request.form['checkout_time']
                n_baules = request.form['n_baules']
                cursor.execute("""INSERT INTO propiedades (nombre,direccion,n_camas_matrimonio,n_camas_individuales,n_banyos,capacidad_guests,idusuario,idairbnb,idbooking,checkin_time,checkout_time,n_baules) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(nombre,direccion,n_matrimonio,n_individuales,n_banyos,capacidad_guests,idusuario,idairbnb,idbooking,checking_time,checkout_time,n_baules))
                cursor.connection.commit()
                flash("Se ha insertado la propiedad con éxito!","success")

            return render_template("anyadirpropiedad.html",nombre=nom)

    return  redirect(url_for("login"))



@application.route("/administracion")
def administracion():
    if 'loggedin' in session:
        if session['permisos'] == "1":
            nom = session["gestoria"]
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM usuarios")
            resultado = cursor.fetchall()
            cursor.close()
            return render_template("administracion.html",resultado = resultado,nombre=nom)

        else:
            return redirect(url_for("inside"))
    return redirect(url_for("login"))

@application.route("/reservas")
def reservas():
    tod = datetime.now()
    diaa = str(tod).split()
    dia_def = diaa[0]
    hora = str(tod).split(":")
    horaa = hora[0].split()
    hora_def = horaa[1]

    if 'loggedin' in session:
        if session['permisos'] == "1":
            cursor = mysql.connection.cursor()
            cursor2 = mysql.connection.cursor()
            nom = session["gestoria"]
            cursor.execute("TRUNCATE TABLE reservas")
            cursor.execute("TRUNCATE TABLE reservas_showing")
            cursor.execute("SELECT * FROM airbnb")
            air = cursor.fetchall()
            for u in air:
                importacio_airbnb.reservas(u["email"],u["password"],u["idusuario"],u["token"])
            cursor.execute("SELECT * FROM reservas")
            res = cursor.fetchall()
            for reserva in res:
                cursor.execute("SELECT * FROM propiedades WHERE idairbnb = %s",[reserva["idpropiedad"]])
                prop = cursor.fetchone()
                if prop != None:
                    cursor.execute("""INSERT INTO reservas_showing (direccion_reservas,fecha_checkin,fecha_checkout,precio,n_guests,idusuario_reservas,idpropiedad_reservas,fecha_reserva,nombre,direccion_propiedades,n_camas_matrimonio,n_camas_individuales,n_banyos,capacidad_guests,idusuario_propiedades,idairbnb,idbooking,checkout_time,checkin_time,n_baules) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(reserva["direccion"],reserva["fecha_checkin"],reserva["fecha_checkout"],reserva["precio"],reserva["n_guests"],reserva["idusuario"],reserva["idpropiedad"],reserva["fecha_reserva"],prop["nombre"],prop["direccion"],prop["n_camas_matrimonio"],prop["n_camas_individuales"],prop["n_banyos"],prop["capacidad_guests"],prop["idusuario"],prop["idairbnb"],prop["idbooking"],prop["checkin_time"],prop["checkout_time"],prop["n_baules"]))
                    cursor2.execute("""INSERT INTO historico_reservas (direccion_reservas,fecha_checkin,fecha_checkout,precio,n_guests,idusuario_reservas,idpropiedad_reservas,fecha_reserva,nombre,direccion_propiedades,n_camas_matrimonio,n_camas_individuales,n_banyos,capacidad_guests,idusuario_propiedades,idairbnb,idbooking,checkout_time,checkin_time,n_baules,dia_reserva_sacada,hora_reserva_sacada) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(reserva["direccion"],reserva["fecha_checkin"],reserva["fecha_checkout"],reserva["precio"],reserva["n_guests"],reserva["idusuario"],reserva["idpropiedad"],reserva["fecha_reserva"],prop["nombre"],prop["direccion"],prop["n_camas_matrimonio"],prop["n_camas_individuales"],prop["n_banyos"],prop["capacidad_guests"],prop["idusuario"],prop["idairbnb"],prop["idbooking"],prop["checkin_time"],prop["checkout_time"],prop["n_baules"],str(dia_def),str(hora_def)))
                    cursor2.connection.commit()
                else:
                    cursor.execute("""INSERT INTO reservas_showing (direccion_reservas,fecha_checkin,fecha_checkout,precio,n_guests,idusuario_reservas,idpropiedad_reservas,fecha_reserva) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",(reserva["direccion"],reserva["fecha_checkin"],reserva["fecha_checkout"],reserva["precio"],reserva["n_guests"],reserva["idusuario"],reserva["idpropiedad"],reserva["fecha_reserva"]))
                    cursor2.execute("""INSERT INTO historico_reservas (direccion_reservas,fecha_checkin,fecha_checkout,precio,n_guests,idusuario_reservas,idpropiedad_reservas,fecha_reserva,dia_reserva_sacada,hora_reserva_sacada) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(reserva["direccion"],reserva["fecha_checkin"],reserva["fecha_checkout"],reserva["precio"],reserva["n_guests"],reserva["idusuario"],reserva["idpropiedad"],reserva["fecha_reserva"],str(dia_def),str(hora_def)))
                    cursor2.connection.commit()
            cursor.execute("SELECT * FROM reservas_showing")
            resultat = cursor.fetchall()
#("""INSERT INTO usuarios (email,password,nombre_gestoria,primeruso,permisos) VALUES (%s,%s,%s,%s,%s)""",(email,password2,username,"1","2"))

            cursor.close()
            return render_template("reservas.html",air=air,res=res,nombre=nom,resultat = resultat)
        else:
            return redirect(url_for("inside"))
    return redirect(url_for("login"))

@application.route("/tablas_admin")
def tablas_admin():
    if 'loggedin' in session:
        if session['permisos'] == "1":
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM propiedades")
            prop = cursor.fetchall()
            return render_template("tablas.html",propiedades = prop)
    return redirect(url_for("login"))



@application.route("/logout")
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('email',None)
    return redirect(url_for('login'))






if __name__ == "__main__":
    application.run(host="0.0.0.0",port=8080,debug=True)
    application.run(debug=True)