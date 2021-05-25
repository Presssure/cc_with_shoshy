from app import app

from flask import render_template, request, redirect, jsonify, make_response, session, url_for, flash

from datetime import datetime

from decimal import Decimal

from pprint import pprint

from botocore.exceptions import ClientError

import json

import boto3

import logging

import requests
# import urllib.request

from boto3.dynamodb.conditions import Key, Attr

import os
app.secret_key="uruKZqxipteEP5_KiRerSQ"

def put_login(email, password, username, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cc-a3-login')
    response = table.put_item(
        Item={
            'email': email,
            'password': password,
            'username': username
            }
    )
    return response

def get_login(email, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cc-a3-login')
    try:
        print("email:  ",email)
        response = table.get_item(Key={'email': email})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response.get('Item')


@app.route("/")
def index():
    print("hello")
    return render_template("index.html")

@app.route("/about")
def about():
    print("hello")
    return "about page created by shoshy and his bae"
    
@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():

    if request.method=="POST":
        req=request.form
        email=req.get("email")
        password=req.get("password")
        user=get_login(email)
        if user != None:
            if user['password']==password:
                session["USERNAME"]=user["username"]
                session["EMAIL"]=email
                print("User added to session")
                return redirect(url_for("profile"))
            else:
                flash("email or password is invalid")
        else:
            flash("email or password is invalid")
        
    return render_template("sign_in.html")


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method =="POST":
        req=request.form
        # 3 wyas to get data from a form but .get is the best as it will return none if it doesn't find the element and doesn't error out
        username=req["username"]
        email=req.get("email")
        password=request.form["password"]
        isUnique=True
        if get_login(email)!=None:
            isUnique=False
            flash("The email already exists")
        else:
            put_login(email, password, username)
            return redirect(url_for("sign_in"))
    return render_template("sign_up.html")

@app.route("/logout")
def logout():
    session.pop("USERNAME", None)
    return redirect(url_for("sign_in"))


@app.route("/profile", methods=["GET","POST"])
def profile():
    user=None
    if session.get("USERNAME", None) is not None:
        username=session.get("USERNAME")
        email=session.get("EMAIL")
        user=get_login(email)
        return render_template("profile.html", user=user)
    else:
        print("Username not found in session")
        return redirect(url_for("sign_in"))

@app.route("/forum", methods=["GET", "POST"])
def forum():
    user=None
    if session.get("USERNAME", None) is not None:
        username=session.get("USERNAME")
        email=session.get("EMAIL")
        user=get_login(email)
        return render_template("forum.html", user=user)
    else:
        print("Username not found in session")
        return redirect(url_for("sign_in"))

@app.route("/suggestion", methods=["GET", "POST"])
def suggestion():
    user=None
    # URL="https://jdlzgl06s9.execute-api.us-east-1.amazonaws.com/my-function"
    URL="https://mva5kr1vbd.execute-api.us-east-1.amazonaws.com/RDSQuery"
    headers={"Content-Type": "application/json"}
    params={"qs": "somevalue"}
    payload={"payload": "Shoshy"}
    if session.get("USERNAME", None) is not None:
        username=session.get("USERNAME")
        email=session.get("EMAIL")
        user=get_login(email)
        r=requests.request("GET", URL, params=params, headers=headers)
        # r=requests.request("POST", URL, headers=headers, data=payload)
        print(r.text)
        return render_template("suggestion.html", user=user)
    else:
        print("Username not found in session")
        return redirect(url_for("sign_in"))

