from flask import Blueprint, Flask, request, jsonify
from db import mysql
import json
from auth import auth, jsonFormatArray, jsonFormat, tokenKey, dateFormat, mail
from datetime import datetime, timedelta
import googlemaps
from key import API_KEY
import math
import requests


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
    return "BUTUH INFORMASI?"

@app.route('/hotel', methods=['GET', 'POST'])
def hotel1():
    cursor = mysql.connection.cursor()
    if (request.method == 'GET'):
        Nama_Hotel = request.args.get('Nama_Hotel')
        Bintang = request.args.get('Bintang')
        id = request.args.get('Id')
        re = request.args.get('Type')
        resto = 0
        cafe = 0
        warung = 0
        rm = 0
        ayce = 0
        dll = 0
        print(Nama_Hotel,Bintang,id)
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

        elif(id):
            query = "SELECT * FROM hotel WHERE id={} ".format(id)
            cursor.execute(query)
            data = jsonFormat(cursor)
            print(data)

            fnbData = getFnbData()
            fnbList = []
            payload = {"hotel":data}

            for item in fnbData:
    
                if (item['titik_koordinat']):
                    titik = item['titik_koordinat']
                    lat1 = (titik.split(',')[0])
                    long1 = (titik.split(', ')[1])
                    print(float(data['latitude']), float(data['longitude']), float(lat1), float(long1))
                    if (not isOverOneKm(float(data['latitude']), float(data['longitude']), float(lat1), float(long1))):
                
                        if (item['kategori'] == 'Restoran'):
                            resto += 1
                        elif (item['kategori'] == 'Cafe'):
                            cafe += 1
                        elif (item['kategori'] == 'Warung'):
                            warung += 1
                        elif (item['kategori'] == 'Rumah Makan'):
                            rm += 1
                        elif (item['kategori'] == 'AYCE'):
                            ayce += 1
                        elif (item['kategori'] == 'DLL'):
                            dll += 1
    
                        fnbList.append(item)


            if (fnbList != []):
                payload = {
                    "hotel": data,
                    "fnb_terdekat": fnbList
                }
            
            if (re == 'kategori'):
                payload = {
                    "hotel": data,
                    "jumlah": {
                        "Restoran": resto,
                        "Cafe": cafe,
                        "Warung": warung,
                        "Rumah Makan": rm,
                        "AYCE": ayce,
                        "DLL": dll
                    }
                }

            return jsonify(payload)

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


# def getLatLong(street):
#     gmaps_key = googlemaps.Client(key=API_KEY)
#     g = gmaps_key.geocode(street)
#     lat = g[0]["geometry"]["location"]["lat"]
#     long = g[0]["geometry"]["location"]["lng"]
#     if (lat and long):
#         print('Latitude: ', lat, ', Longitude: ', long, str(lat+long))
#         return ({"latitude": lat, "longitude": long})
#     else: 
#         return {}

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

def getFnbData():
    response = requests.get('http://20.213.139.144/fnb')

    data = response.json()
    return data


def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to spherical coordinates in radians.
    rlat1 = math.radians(lat1)
    rlon1 = math.radians(lon1)
    rlat2 = math.radians(lat2)
    rlon2 = math.radians(lon2)

    # Compute the Haversine distance
    dlon = rlon2 - rlon1
    dlat = rlat2 - rlat1
    a = math.sin(dlat / 2)**2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Convert the distance from radians to kilometers
    km = 6371 * c

    return km

def isOverOneKm(lat1, lon1, lat2, lon2):
    distance = haversine(lat1, lon1, lat2, lon2)
    if distance <= 1:
        return(False)
    return(True)
        


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)
    