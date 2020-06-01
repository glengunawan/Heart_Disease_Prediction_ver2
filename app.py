from flask import Flask, render_template, url_for, jsonify, request
import pandas as pd 
import numpy as np 
import mysql.connector 
import requests
from tensorflow import keras 

dbku = mysql.connector.connect( 
    host = 'localhost', 
    port = '3306', 
    user = 'root', 
    passwd = 'tenebrae',
    database = 'testestes'
)

app = Flask(__name__) 

# model = keras.models.load_model('./model2/trained_heart_model.h5')

# ---Login---

@app.route('/', methods=['GET', 'POST']) 
def home():  
    if request.method == 'GET':
        return render_template('login.html') 
    elif request.method == 'POST': 
        username = request.form['username']
        password = request.form['password']

        x = dbku.cursor(dictionary=True) 

        query = 'select * from ListUser' 
        x.execute(query) 

        tampungUser = list(x) 
        listUsername = []  
        listPassword = []  

        for i in tampungUser: 
            listUsername.append(i['Nama'])
            listPassword.append(i['Password'])

        if username in listUsername and password == listPassword[listUsername.index(username)]:
            # return redirect(url_for('form', user=username))
            return render_template('form.html')
        else:
            return render_template('error_login.html')

# ---Signup---

@app.route('/signup', methods=['GET', 'POST']) 
def signup():  
    if request.method == 'GET':
        return render_template('signup.html') 
    elif request.method == 'POST': 
        username = request.form['username']
        password = request.form['password']

        x = dbku.cursor(dictionary=True) 

        query = 'select * from ListUser' 
        x.execute(query) 

        tampungUser = list(x) 
        listUsername = []  
        listPassword = []  

        for i in tampungUser: 
            listUsername.append(i['Nama'])

        if username in listUsername:
            return render_template('error_signup.html')
        else:
            dataUser = (username, password)
            query = 'CREATE TABLE IF NOT EXISTS ListUser (Nama varchar(50), Password varchar(50));'
        
            x = dbku.cursor()
            x.execute(query) 

            queryku = 'insert into ListUser (Nama, Password) values(%s, %s)' 
            x.execute(queryku, dataUser) 
            dbku.commit()

            return render_template('proceed_signup.html')

@app.route('/form/<string:user>')
def form(user):
    return render_template('form.html', user=user) 

# @app.route('/result', methods=['POST'])
# def result():
#     return render_template('result.html', user=user) 



if __name__ == '__main__': 
    app.run(debug=True)