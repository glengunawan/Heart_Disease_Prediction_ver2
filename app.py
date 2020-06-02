import pandas as pd 
import numpy as np 
from flask import Flask, render_template, url_for, jsonify, request, redirect
import mysql.connector 
import requests
from tensorflow import keras 
from sklearn.preprocessing import MinMaxScaler
from pickle import load

dbku = mysql.connector.connect( 
    host = 'localhost', 
    port = '3306', 
    user = 'root', 
    passwd = 'tenebrae',
    database = 'testestes'
)

app = Flask(__name__) 

# ---Login---

@app.route('/', methods=['GET', 'POST']) 
def home():  
    if request.method == 'GET':
        return render_template('login.html') 
    elif request.method == 'POST': 
        nama_pasien = request.form['name'].upper()
        id_pasien = request.form['id']

        data_pasien = {'nama': nama_pasien, 'id': id_pasien}

        x = dbku.cursor()
        query = 'CREATE TABLE IF NOT EXISTS PatientList (name varchar(50), patientID varchar(50));'
        x.execute(query) 

        x = dbku.cursor(dictionary=True) 
        query = 'select * from PatientList' 
        x.execute(query) 

        tampungPasien = list(x) 
        listNama = []  
        listID = []  

        for i in tampungPasien: 
            listNama.append(i['name'])
            listID.append(i['patientID'])


        if nama_pasien in listNama and id_pasien == listID[listNama.index(nama_pasien)]:
            return render_template('form.html', patient=data_pasien)
        else:
            return render_template('error_login.html')

# ---Signup---

@app.route('/signup', methods=['GET', 'POST']) 
def signup():  
    if request.method == 'GET':
        return render_template('signup.html') 
    elif request.method == 'POST': 
        name = request.form['name'].upper()
        patientID = request.form['id']
        
        x = dbku.cursor()
        query = 'CREATE TABLE IF NOT EXISTS PatientList (name varchar(50), patientID varchar(50));'
        x.execute(query) 

        x = dbku.cursor(dictionary=True) 

        query = 'select * from PatientList' 
        x.execute(query) 

        tampungPasien = list(x) 
        listPasien = []  
        listID = []  

        for i in tampungPasien: 
            listPasien.append(i['name'])

        if name in listPasien:
            return render_template('error_signup.html')
        else:
            dataPasien = (name, patientID)

            queryku = 'insert into PatientList (name, patientID) values(%s, %s)' 
            x.execute(queryku, dataPasien) 
            dbku.commit()

            return render_template('proceed_signup.html')

# --Form--

# @app.route('/form/<string:user>')
# def form(user):
#     return render_template('form.html', user=user) 

@app.route('/predict', methods=['POST'])
def predict():
    body = request.form 

    name = body['user'].upper()
    age = int(body['age'])
    sex = int(body['sex'])
    cp = int(body['cp'])
    trestbps = int(body['trestbps'])
    chol = int(body['chol'])
    fbs = int(body['fbs'])
    restecg = int(body['restecg'])
    thalach = int(body['thalach'])
    exang = int(body['exang'])
    oldpeak = float(body['oldpeak'])
    slope = int(body['slope'])
    ca = int(body['ca'])
    thal = int(body['thal']) 

    list_data = [[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]]
    dfData = pd.DataFrame(list_data)
    print(dfData)

    # Ambil ID
    tuple_name = (name,)
    # print(tuple_name)
    x = dbku.cursor(dictionary=True) 
    query = 'select patientID from PatientList where name = %s' 
    x.execute(query, tuple_name) 
    id_pasien = list(x)
    # print(id_pasien)
    id_pasien = id_pasien[0]['patientID']
    
    # Data Normalization and Preprocessing
    scaler = load(open('scaler.pkl', 'rb'))
    data_scale = scaler.transform(dfData) 
    list_data_scale = list(data_scale) 
    print(list_data_scale)
    
    list_tampung = []
    for i in list_data_scale[0]: 
        list_tampung.append(i)
    dfData_scale = pd.DataFrame([list_tampung])
    print(dfData_scale)

    # Model Prediction 
    model = keras.models.load_model('./model2/trained_heart_model.h5')
    prediction = model.predict_classes(dfData_scale)
    probability = model.predict(dfData_scale) 

    #Untuk Webpage
    tuple_data = (name, id_pasien, age, sex, cp, trestbps, chol, 
                fbs, restecg, thalach, exang, oldpeak, slope, 
                ca, thal, prediction[0], probability[0][0])

    #Khusus untuk SQL
    tuple_data2 = (name, id_pasien, age, sex, cp, trestbps, chol, 
                fbs, restecg, thalach, exang, oldpeak, slope, 
                ca, thal, int(prediction[0]), float(probability[0][0]))

    querytable = 'CREATE TABLE IF NOT EXISTS ListData3 (name varchar(50), id varchar(50), age int, sex int, cp int, trestbps int, chol int, fbs int, restecg int, thalach int, exang int, oldpeak float, slope int, ca int, thal int, pred int, proba float);'
    x = dbku.cursor()
    x.execute(querytable) 
    dbku.commit()

    querydata = 'INSERT INTO ListData3 values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    x.execute(querydata, tuple_data2) 
    dbku.commit()

    # Ubah data untuk ditampilkan di HTML
    list_column = ['name', 'id', 'age', 'sex', 'cp', 'trestbps', 'chol', 
                    'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 
                    'slope', 'ca', 'thal', 'prediction', 'probability']

    list_data_lengkap = list(tuple_data) 

    tampung_zip = zip(list_column, list_data_lengkap) 
    dict_data = dict(tampung_zip)

    return render_template('prediction.html', data=dict_data)

@app.route('/history', methods=['GET', 'POST'])
def history():  
    
    if request.method == 'GET':
        return render_template('login_history.html') 
    elif request.method == 'POST': 
        nama_pasien = request.form['name'].upper()
        id_pasien = request.form['id']
        data_pasien = {'nama': nama_pasien, 'id': id_pasien}

        tuple_id = (id_pasien,)
        x = dbku.cursor(dictionary=True) 
        query = 'select * from listData3 where id = %s' 
        x.execute(query, tuple_id) 
        data_pasien = list(x)
        data = pd.DataFrame(data_pasien)

        # print(data)

        x = dbku.cursor(dictionary=True) 
        query = 'select * from PatientList' 
        x.execute(query) 

        tampungPasien = list(x) 
        listNama = []  
        listID = []  

        for i in tampungPasien: 
            listNama.append(i['name'])
            listID.append(i['patientID'])


        if nama_pasien in listNama and id_pasien == listID[listNama.index(nama_pasien)]:
            return render_template('history.html',  tables=[data.to_html()], titles=data.columns.values, pasien = data_pasien)
        else:
            return render_template('error_history.html')

if __name__ == '__main__': 
    app.run(debug=True)