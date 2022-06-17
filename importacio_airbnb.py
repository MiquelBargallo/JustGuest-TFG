from application import mysql
from resources import airbnb

def reservas(usuario,contrasenya,id_usuario,token):
        exit = 1
        reserva = {}
        if token == None:
            try:
                api = airbnb.Api(usuario,contrasenya)
                tokenn = api.access_token()
                cursor1 = mysql.connection.cursor()
                cursor1.execute("UPDATE airbnb SET token = %s WHERE idusuario = %s",(tokenn,id_usuario))
                cursor1.execute("SELECT * FROM airbnb WHERE idusuario = %s",id_usuario)
                result = cursor1.fetchone()
                tok = result["token"]
                api = airbnb.Api(access_token=tok)
                cursor1.connection.commit()
                reserva = api.get_Reservation()
            except:
                pass
        else:
            api = airbnb.Api(access_token=token)
            try:
                reserva = api.get_Reservation()
            except:
                try:
                    api = airbnb.Api(usuario, contrasenya)
                    tokenn = api.access_token()
                    cursor1 = mysql.connection.cursor()
                    cursor1.execute("UPDATE airbnb SET token = %s WHERE idusuario = %s", (tokenn, id_usuario))
                    cursor1.execute("SELECT * FROM airbnb WHERE idusuario = %s", id_usuario)
                    result = cursor1.fetchone()
                    tok = result["token"]
                    api = airbnb.Api(access_token=tok)
                    cursor1.connection.commit()
                    reserva = api.get_Reservation()
                except:

                    exit = 0
                    pass
        if exit == 1:
            if reserva["reservations"] != []:
                for res in reserva["reservations"]:
                    direccion = res["listing"]["full_address"]
                    check_in = res["check_in"]
                    check_out = res["check_out"]
                    precio = res["host_price_breakdown"]["host_payout_breakdown"]["total"]["amount_formatted"]
                    n_guests = res["guest_details"]["localized_description"]
                    idusuario = id_usuario
                    idpropiedad = res['listing']['id']
                    book_at = res["booked_at"].split("T")
                    fecha_reserva = book_at[0]
                    cursor = mysql.connection.cursor()
                    cursor.execute("""INSERT INTO reservas (direccion,fecha_checkin,fecha_checkout,precio,n_guests,idusuario,idpropiedad,fecha_reserva) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) """,(direccion,check_in,check_out,precio,n_guests,idusuario,idpropiedad,fecha_reserva))
                    cursor.close()


            else:
                pass
        else:
            pass


