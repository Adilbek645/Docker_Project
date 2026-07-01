from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3


app = Flask(__name__)

@app.route("/")
def forgery():
    return render_template("forgery.html")

@app.route("/auction")
def auction():
    return render_template("auction.html")

@app.route("/shop")
def shop():
    return render_template("shop.html")

@app.route("/guild")
def guild():
    return render_template("guild.html")

@app.route("/upgrades")
def upgrades():
    return render_template("upgrades.html")

app.run(host="0.0.0.0", port=5000)