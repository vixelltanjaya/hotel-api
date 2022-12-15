from flask import Blueprint, Flask, request, jsonify
from db import mysql
import json
from auth import auth, jsonFormatArray, jsonFormat, tokenKey, dateFormat, mail
from datetime import datetime, timedelta


app = Flask(__name__)

app.register_blueprint(auth)

app.config["SECRET_KEY"]= "secret"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'vixell'
app.config['MYSQL_DB'] = 'hotel_api'
# app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'

app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "imap.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_DEFAULT_SENDER"] = "18220060@std.stei.itb.ac.id"
app.config["MAIL_USERNAME"] = "18220060@std.stei.itb.ac.id"
app.config["MAIL_PASSWORD"] = "xihxreqtstdauada"

mysql.init_app(app)
mail.init_app(app)

@app.route('/', methods=['GET'])
def hotel():
    return "BUTUH INFORMASI?"

@app.route('/hotel', methods=['GET', 'POST'])
def hotel1():
    print()
    cursor = mysql.connection.cursor()
    if (request.method == 'GET'):
        Nama_Hotel = request.args.get('Nama_Hotel')
        Bintang = request.args.get('Bintang')
        # Klasifikasi_Hotel = request.args.get('Klasifikasi_Hotel')
        # Alamat_Hotel = request.args.get('Alamat_Hotel')
        # Jumlah_Kamar = request.args.get('Jumlah_Kamar')
        if (Nama_Hotel and Bintang):
            query = "SELECT * FROM hotel WHERE Nama_Hotel LIKE '%{}%' AND Bintang LIKE '%{}%' ".format(Nama_Hotel, Bintang)
            cursor.execute(query)
            data = cursor.fetchall()
            return jsonify(data)

        elif(Bintang):
            query = "SELECT * FROM hotel WHERE Bintang LIKE '%{}%' ".format(Bintang)
            cursor.execute(query)
            data = cursor.fetchall()
            return jsonify(data)

        elif(Nama_Hotel):
            query = "SELECT * FROM hotel WHERE Nama_Hotel LIKE '%{}%' ".format(Nama_Hotel)
            cursor.execute(query)
            data = cursor.fetchall()
            return jsonify(data)

        else:
            cursor = mysql.connection.cursor()
            query = "SELECT * FROM hotel"
            cursor.execute(query)
            data = cursor.fetchall()

            return jsonify(data)

    elif (request.method == 'POST'):
        json_data = request.json
        data = {
            "Nama_Hotel": json_data['Nama_Hotel'],
            "Bintang": json_data['Bintang'],
            "Klasifikasi_Hotel": json_data['Klasifikasi_Hotel'],
            "Alamat_Hotel": json_data['Alamat_Hotel'],
            "Jumlah_Kamar": json_data['Jumlah_Kamar'],
        }
        cursor.execute(' INSERT INTO hotel(Nama_Hotel, Bintang, Klasifikasi_Hotel, Alamat_Hotel, Jumlah_Kamar) VALUES (%s, %s, %s, %s, %s)', (data["Nama_Hotel"], data["Bintang"], data["Klasifikasi_Hotel"], data["Alamat_Hotel"], data["Jumlah_Kamar"]))

        mysql.connection.commit()
        return "Data Berhasil Dibuat", 201

@app.route('/hotel/<int:id>', methods=['PUT', 'DELETE'])
def hotel2(id):
    print(id)
    cursor = mysql.connection.cursor()

    if (request.method == 'PUT'):        
        json_data = request.json
        data = {
            "Nama_Hotel": json_data['Nama_Hotel'],
            "Bintang": json_data['Bintang'],
            "Klasifikasi_Hotel": json_data['Klasifikasi_Hotel']  ,
            "Alamat_Hotel": json_data['Alamat_Hotel'],
            "Jumlah_Kamar": json_data['Jumlah_Kamar'],
        }
        cursor.execute('UPDATE hotel SET Nama_Hotel=%s, Bintang=%s, Klasifikasi_Hotel=%s, Alamat_Hotel=%s, Jumlah_Kamar=%s WHERE id=%s', (data["Nama_Hotel"], data["Bintang"], data["Klasifikasi_Hotel"], data["Alamat_Hotel"], data["Jumlah_Kamar"], id))

        mysql.connection.commit()
        return jsonify(data), 204

    elif (request.method == 'DELETE'): 
        cursor.execute('DELETE FROM hotel WHERE id=%s', (id,))
        mysql.connection.commit()

        return jsonify({"messages": "Data Berhasil Dihapus"}), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)
    