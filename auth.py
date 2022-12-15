from flask import Blueprint, jsonify, request, make_response, session
from db import mysql
from flask_mail import Message, Mail
from datetime import datetime, timedelta
import jwt
import bcrypt
import secrets
import re

key = 'mamapapalarang'
tokenKey = 'mimpiadalahkunci'
dateFormat = '%Y-%m-%dT%H:%M:%S'

mail = Mail()

# ePass --> enteredPassword
# cPass --> currentPassword
def encodeStr(ePass):
    hashed_password = bcrypt.hashpw((key+ePass).encode("utf-8"), bcrypt.gensalt())
    return hashed_password

def verifyUser(ePass, cPass):
    return bcrypt.checkpw((key+ePass).encode("utf-8"), cPass.encode("utf-8"))

def otpHandler(data):
    otp = secrets.token_hex(3)
    ses = session.get('session')
    
    payload = {
        'data': data,
        'otp': otp
    }

    if (ses):
        for item in ses:
            if (item['data'] == data):
                return "OTP sudah berhasil dikirimkan, silahkan cek pada email anda"
        ses.append(payload)
        session['session'] = ses

    else:
        session['session'] = [payload]

    msg = Message("Your OTP, ", recipients=[data['email']])
    msg.body = f"OTP anda: {otp}"
    mail.send(msg)

    return "Berhasil mengirimkan OTP! Silahkan cek email anda"

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

def checkToken(bearer):
    try:
        token = bearer.split()[1]
        decodedToken = jwt.decode(token, tokenKey, algorithms=['HS256'])
        date_str = decodedToken['exp_date']
        tokenDate = datetime.strptime(date_str, dateFormat)
        if (tokenDate < datetime.now()):
            raise

        return True
    except:
        return False

auth = Blueprint('auth', __name__)

@auth.route('/daftar', methods=['POST'])
def daftar():
    cursor = mysql.connection.cursor()
    json_data = request.json

    data = {
        "email": json_data['email'],
        "password": json_data['password'],
    }

    otp = request.args.get('otp')
    if (otp):
        return checkOTP(otp, data['email'])

    if not validEmail(data['email']):
        return "Silahkan Masukkan Email yang Valid", 401

    if checkUserAvailable(cursor, data):
        return "Email anda sudah digunakan", 401

    else:

        res = otpHandler(data)

        return res, 200

def checkOTP(otp, email):
    print(email)
    ses = session.get('session')
    if (ses):
        for item in ses:
            sessionEmail = item['data']['email']
            sessionOtp = item['otp']
            if (sessionEmail == email):
                print(sessionEmail, email, otp, sessionOtp)
                if (otp == sessionOtp):
                    try:
                        createUser(item['data'])
                        newSes = filter(lambda x: x != item, ses)
                        session['session'] = list(newSes)
                    except:
                        return "Gagal untuk membuat akun", 400
                    
                    return "Akun berhasil dibuat", 201

                else: 
                    return "OTP SALAH", 200

    return "Pastikan anda sudah daftar", 400

def createUser(data):
    cursor = mysql.connection.cursor()
    encodedPass = encodeStr(data['password'])

    cursor.execute(' INSERT INTO akun(email, password) VALUES (%s, %s) ', (data['email'], encodedPass))

    mysql.connection.commit()
    cursor.close()
    


@auth.route('/login', methods=['POST'])
def login():
    cursor = mysql.connection.cursor()
    json_data = request.json

    data = {
        "email": json_data['email'],
        "password": json_data['password'],
    }

    cursor.execute(' SELECT * FROM akun WHERE email=%s ', (data['email'],))
    resUser = jsonFormat(cursor)

    if (resUser):
        if (verifyUser(data['password'], resUser['password'])):
            date = datetime.now() + timedelta(days=7)
            date_str = date.strftime(dateFormat)
            token = jwt.encode({'exp_date' : date_str}, tokenKey)

            return jsonify(
                {
                'message': 'Gunakan token ini untuk akses API kami', 
                'token' : token
                }), 201
        else:
            return "Email atau Password SALAH", 401
            
    return "Email tidak ditemukan, Silahkan Daftarkan akun anda", 404


def checkUserAvailable(cursor, data):
    cursor.execute('SELECT * FROM akun WHERE email=%s', (data['email'],))
    res = jsonFormat(cursor)

    return res

def checkSessionAvailable(cursor, data):
    print(cursor,data)
    res = 0
    if (data != {}):
        cursor.execute(' SELECT * FROM session WHERE user_id=%s ', (data['id'],))
        res = jsonFormat(cursor)

    return res 

def validEmail(email):
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(regex, email):
        return True
    return False

@auth.route('/clear')
def clear():
    session.clear()
    return "Mengakhiri session!", 200

@auth.route('/check')
def check():
    return jsonify(session), 200




