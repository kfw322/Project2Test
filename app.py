import pandas as pd
import numpy as np
import os
import sqlalchemy
import pymysql
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Text, Float
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import matplotlib.pyplot as plt
from flask import Flask, jsonify, render_template, request, redirect
import json

pymysql.install_as_MySQLdb()
engine = create_engine("mysql://root:root@localhost:3306/Dump20180614")
#engine.execute("USE Dump20180614")
conn = engine.connect()
Base= automap_base()
Base.prepare(engine,reflect=True)
Base.classes.keys()
inspector=inspect(engine)
inspector.get_table_names()
inspector.get_columns("disposable_personal_income")

class datatable1(Base):
    __tablename__ = "table_uno"
    __table_args__ = {"extend_existing":True}
    nameofprimarykey = Column(Text,primary_key=True)

Base.prepare()
session=Session(engine)
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/statelist")
def statelist():
    raw_df = pd.read_csv("PCE_ALL_AREAS (1).csv")
    raw_df["GeoFIPS"] = pd.to_numeric(raw_df["GeoFIPS"],errors="coerce")
    df=raw_df.loc[raw_df["GeoFIPS"].between(1,60000, inclusive=False)] #leaving out all the region data and national data... states only
    statelist = sorted(df["GeoName"].value_counts().reset_index()["index"].tolist())
    return(statelist)

@app.route("/pce/<state>")
def pce(state):
    pce_data_dict = {}
    #code to read in pce by state info
    return(jsonify(pce_data_dict))

@app.route("/savings/<state>")
def pce(state):
    #code to read in pce by state info
    raw_df = pd.read_csv("PCE_ALL_AREAS (1).csv")
    raw_df["GeoFIPS"] = pd.to_numeric(raw_df["GeoFIPS"],errors="coerce")
    df=raw_df.loc[raw_df["GeoFIPS"].between(1,60000, inclusive=False)] #leaving out all the region data and national data... states only
    statelist = sorted(df["GeoName"].value_counts().reset_index()["index"].tolist())
    df_dict = {} #dict of dataframes
    datadict = {} #dict json
    for state in statelist:
        df_dict[state] = df.loc[df["GeoName"]==state].reset_index(drop=True)
        datadict[state]={} 
        for year in range(1997,2017,1):
            y=str(year)
            datadict[state][y]={}
            datadict[state][y]["Total PCE"] = df_dict[state].at[0,f"{year}"]
            datadict[state][y]["Goods"] = df_dict[state].at[1,f"{year}"]
            datadict[state][y]["Services"] = df_dict[state].at[12,f"{year}"]
    savings_data_dict = datadict
    with open('pcebystatebyyear.json', 'w') as outfile:
        json.dump(datadict, outfile, sort_keys = True, indent = 4, ensure_ascii = False)
    return(jsonify(savings_data_dict))

if __name__ == "__main__":
    app.run(debug=True)