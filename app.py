from flask import Blueprint, Flask, request, jsonify
from db import mysql
import json
from auth import auth, jsonFormatArray, jsonFormat, tokenKey, dateFormat, mail
from datetime import datetime, timedelta
import googlemaps
from key import API_KEY


app = Flask(__name__)

app.register_blueprint(auth)

app.config["SECRET_KEY"]= "secret"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'hotel_api'

#keperluan testing
app.config['MYSQL_DB'] = 'TUBES'
app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'

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
    getLatLong()
    return "BUTUH INFORMASI?"

@app.route('/hotel', methods=['GET', 'POST'])
def hotel1():
    print()
    cursor = mysql.connection.cursor()
    if (request.method == 'GET'):
        Nama_Hotel = request.args.get('Nama_Hotel')
        Bintang = request.args.get('Bintang')
        # Klasifikasi_Hotel = request.args.get('Klasifikasi_Hotel')
        Alamat_Hotel = request.args.get('Alamat_Hotel')
        # Jumlah_Kamar = request.args.get('Jumlah_Kamar')
        if (Nama_Hotel and Bintang):
            query = "SELECT * FROM hotel WHERE Nama_Hotel LIKE '%{}%' AND Bintang LIKE '%{}%' ".format(Nama_Hotel, Bintang)
            cursor.execute(query)
            data = jsonFormatArray(cursor)

            return jsonify(data)
        
        elif(Alamat_Hotel):
            query = "SELECT * FROM hotel WHERE Alamat_Hotel LIKE '%{}%' ".format(Alamat_Hotel)
            cursor.execute(query)
            data = jsonFormatArray(cursor)
            
            return jsonify(data)

        elif(Bintang):
            query = "SELECT * FROM hotel WHERE Bintang LIKE '%{}%' ".format(Bintang)
            cursor.execute(query)
            data = jsonFormatArray(cursor)

            return jsonify(data)

        elif(Nama_Hotel):
            query = "SELECT * FROM hotel WHERE Nama_Hotel LIKE '%{}%' ".format(Nama_Hotel)
            cursor.execute(query)
            data = jsonFormatArray(cursor)

            return jsonify(data)

        else:
            cursor = mysql.connection.cursor()
            query = "SELECT * FROM hotel"
            cursor.execute(query)
            data = jsonFormatArray(cursor)

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

@app.route('/dev/getlatlong', methods=['GET'])
def manipulateDb():
    cursor = mysql.connection.cursor()
    
    cursor.execute('SELECT * FROM hotel')
    hotelData = jsonFormatArray(cursor)

    for hotel in hotelData:
        coor = getLatLong(hotel['Alamat_Hotel'])
        if (coor != {}):
            cursor.execute('UPDATE hotel SET latitude=%s, longitude=%s WHERE id>237', (coor['latitude'], coor['longitude'], hotel['id']))
            mysql.connection.commit()
        else:
            print('lat long NULL', hotel["id"], hotel["Nama_Hotel"])

@app.route('/dev/createcol', methods=['GET'])
def createCol():
    cursor = mysql.connection.cursor()

    cursor.execute('ALTER TABLE hotel ADD latitude VARCHAR(64), ADD longitude VARCHAR(64)')
    mysql.connection.commit()


def getLatLong(street):
    gmaps_key = googlemaps.Client(key=API_KEY)
    g = gmaps_key.geocode(street)
    lat = g[0]["geometry"]["location"]["lat"]
    long = g[0]["geometry"]["location"]["lng"]
    if (lat and long):
        print('Latitude: ', lat, ', Longitude: ', long, str(lat+long))
        return ({"latitude": lat, "longitude": long})
    else: 
        return {}

def jsonFormatArray(cursor):
  headers = [x[0] for x in cursor.description]
  data = cursor.fetchall()

  res = []

  for item in data:
      res.append(dict(zip(headers, item)))

  return res

def jsonFormat(cursor):
  headers = [x[0] for x in cursor.description]
  data = cursor.fetchall()
  res = {}

  for item in data:
    res = (dict(zip(headers, item)))

  return res

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)
    