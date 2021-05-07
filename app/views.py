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


@app.route("/")
def index():
    print("hello")
    

    return render_template("index.html")