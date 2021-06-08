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

import re

import pymysql
app.secret_key="uruKZqxipteEP5_KiRerSQ"

endpoint = 'jenny-database-final.clf9aoosavui.us-east-1.rds.amazonaws.com'
username = 'jenny'
password = 'blackpink'
database_name = 'cc_a3_database'

connection = pymysql.connect(host=endpoint, user=username, password=password, database=database_name)

def find_all_game():
    cursor = connection.cursor()
    cursor.execute('SELECT `name` from `game`')
    rows = cursor.fetchall()
    ret=[]
    for row in rows:
        ret.append(row[0])
    return ret


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

def get_login_api(email):
    URL="https://s7p7uz3gv2.execute-api.us-east-1.amazonaws.com/test/email/"
    params={"qs": "somevalue"}
    headers={"Content-Type": "application/json"}
    r=requests.get(URL+email, headers=headers)
    s=r.text
    s=s[1:-1]
    m=json.loads(s)
    # print(m["name"])
    return m

def put_forum(email, game, subject, message):
    cursor = connection.cursor()
    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(f"INSERT INTO forum_post VALUES ('null', '{subject}', '{message}', '{game}', '{email}', '{time}');")

    connection.commit()
    print("Done!")



def get_forum():
    cursor = connection.cursor()

    cursor.execute('SELECT * from `forum_post` ORDER BY `datetime` DESC')

    rows = cursor.fetchall()

    # for row in rows:
    #     print(f'{row[0]} {row[1]} {row[2]} {row[3]}')
    return rows

def get_replies(id):
    cursor = connection.cursor()

    cursor.execute('SELECT * from `post_reply` ORDER BY `datetime` DESC')

    rows = cursor.fetchall()

    # for row in rows:
    #     print(f'{row[0]} {row[1]} {row[2]} {row[3]}')
    return rows

def get_post(id):
    print(id)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * from `forum_post` where `id`='{id}' ORDER BY `datetime` DESC")
    result = cursor.fetchone()
    print(result)
    return result

def put_replies(email, reply, id):
    cursor = connection.cursor()
    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(f"INSERT INTO post_reply VALUES ('null', '{id}', '{email}','{reply}', '{time}');")
    print("put Reply")
    connection.commit()

def upload_file(file_name, object_name=None):
    if object_name is None:
        object_name=file_name

    s3_client=boto3.client('s3')

    response=s3_client.upload_file(file_name, "game-info-cc-a3-jenny", object_name)

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
        # user=get_login(email)
        user=get_login_api(email)
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
        print(user)
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
        games=find_all_game()
        posts=get_forum()
        if request.method =="POST":
            game=request.form["game"]
            subject=request.form["subject"]
            message=request.form["message"]

            put_forum(email, game, subject, message)
            return redirect(request.url)
        return render_template("forum.html", user=user, games=games, posts=posts)
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

@app.route("/view-post/<post_id>", methods=["GET", "POST"])
def view_post(post_id):
    user=None
    id=post_id
    print("This is the post id: ",post_id)
    if session.get("USERNAME", None) is not None:
        username=session.get("USERNAME")
        email=session.get("EMAIL")
        user=get_login(email)
        post=get_post(post_id)

        if request.method == "POST":
            reply = request.form["reply"]
            put_replies(email, reply, post_id)

        game=post[3]
        subject=post[1]
        message=post[2]
        time=post[5]
        replies=get_replies(id)
        return render_template("view_post.html", id=id,user=user, replies=replies, message=message, time=time,subject=subject, game=game)
    else:
        print("Username not found in session")
        return redirect(url_for("sign_in"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    user=None
    if session.get("USERNAME", None) is not None:
        email=session.get("EMAIL")
        user=get_login(email)
        if request.method=="POST":
            # r=requests.get()
            file=request.files["file"]
            r=requests.get(file, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'})
            with open("game.json", "wb") as f:
                f.write(r.content)
                upload_file("game.json")
        return render_template("admin.html", user=user)

    else:
            print("Username not found in session")
            return redirect(url_for("sign_in"))


# @app.route("/put-reply", methods=["GET","POST"])
# def put_reply():
#     user=None
#     if session.get("USERNAME", None) is not None:
#         username=session.get("USERNAME")
#         email=session.get("EMAIL")
#         user=get_login(email)
#         if request.method =="POST":
#             reply=request.form["reply"]
#             id=request.form["id"]
#             print("post id: ", id)
#             post=get_post(id)
#             print(post)
#             game=post[3]
#             subject=post[1]
#             message=post[2]
#             time=post[5]
#             replies=get_replies(id)
#             put_replies(email, reply, id)
#             print("was here")
#             return redirect()
#     else:
#         print("Username not found in session")
#         return redirect(url_for("sign_in"))