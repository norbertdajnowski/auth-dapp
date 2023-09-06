# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from project.models.voice import voice

from project.models.deploy_contract import contract_addr, web3

voiceObj = voice()

class CreateForm(FlaskForm):
    text = StringField('name', validators=[DataRequired()])


@app.route('/')
def start():
    return render_template('printer/index.html')

@app.route('/about')
def about():
    return render_template('printer/about.html')

@app.route('/login')
def login():
    return render_template('printer/login.html')

@app.route('/register')
def register():
    return render_template('printer/register.html')

@app.route('/delete')
def delete():
    return render_template('printer/delete.html')

@app.route('/addVoice', methods=['GET', 'POST'])
def addVoice():
    voice1 = request.files['voice1'].read()
    voice2 = request.files['voice2'].read()
    voice3 = request.files['voice3'].read()
    username = request.files['username'].read().decode("utf-8") 

    if (voiceObj.add_user(voice1, voice2, voice3, username) == True):
        hash(contract_addr)

    return render_template('printer/index.html')


@app.route('/recognise', methods=['GET', 'POST'])
def recognise():
    voice = request.files['voice1'].read()
    username = request.files['username'].read().decode("utf-8") 
    loginResult = voiceObj.recognise(voice, username)
    print("login result - " + loginResult)
    if loginResult == "Not Found" or loginResult == None:
        return f'We could not identify your account, refresh and try again.'
    elif loginResult == "Username Missing":
        return f'Your username does not exist in the database'
    else:
        return f'Identification completed succesfully!'


@app.route('/deleteVoice', methods=['GET', 'POST'])
def deleteVoice():
    username = request.files['username'].read().decode("utf-8") 
    deleteResult = voiceObj.delete_user(username)
    print("Delete user result - " + deleteResult)
    if deleteResult == "deleted":
        return f'User deleted succesfully'
    elif deleteResult == "No user":
        return f'Username was not found in our database'
    else:
        return f'Problem encountered during user deletion'
    
