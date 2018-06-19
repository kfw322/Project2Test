import pandas as pd
import numpy as np
import os
import sqlalchemy
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Text, Float
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import matplotlib.pyplot as plt
from flask import Flask, jsonify, render_template, request, redirect
import json
from datetime import datetime
from dateutil.parser import parse
import win32api

engine = create_engine("sqlite:///data.sqlite")
conn = engine.connect()
Base= automap_base()
Base.prepare(engine,reflect=True)
Base.classes.keys()
inspector=inspect(engine)
inspector.get_table_names()
inspector.get_columns("DPI")
inspector.get_columns("FPSR")
inspector.get_columns("PCE")
inspector.get_columns("acs2015_county_data")

class DPI(Base):
    __tablename__ = "DPI"
    __table_args__ = {"extend_existing":True}
    field1 = Column(Text,primary_key=True)

class FPSR(Base):
    __tablename__ = "FPSR"
    __table_args__ = {"extend_existing":True}
    DATE = Column(Text,primary_key=True)

class PCE(Base):
    __tablename__ = "PCE"
    __table_args__ = {"extend_existing":True}
    GeoFIPS = Column(Integer,primary_key=True)
    Line = Column(Text,primary_key=True)

class DEMO(Base):
    __tablename__ = "acs2015_county_data"
    __table_args__ = {"extend_existing":True}
    CensusId = Column(Integer,primary_key=True)

Base.prepare()
session=Session(engine)
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/statelist")
def statelist():
    listofstates=[]
    for row in session.query(PCE):
        if int(row.GeoFIPS) < 60000: 
            listofstates.append(row.GeoName)
    statelist = []
    statelist = sorted(list(set(listofstates)))    
    return(jsonify(statelist))

@app.route("/savings")
def savings():
    savings_data_dict = {}
    for row in session.query(FPSR):
        savings_data_dict[str(parse(row.DATE).strftime("%Y-%m-%d"))] = row.USPersonalSavingsRate
    return(jsonify(savings_data_dict))

@app.route("/pce/<state>")
def pce(state):
    datadict = {}
    for year in range (1997,2017,1):
        y=str(year)
        datadict[y] = {}
        sqlquery = str(r' select "' + y + r'" from PCE WHERE GeoName= "' + state + r'" AND Line = "1"')
        for row in conn.engine.execute(sqlquery):
            datadict[y]["Total PCE"] = str(row[0])
        sqlquery = str(r' select "' + y + r'" from PCE WHERE GeoName= "' + state + r'" AND Line = "2"')
        for row in conn.engine.execute(sqlquery):
            datadict[y]["Goods"] = str(row[0])
        sqlquery = str(r' select "' + y + r'" from PCE WHERE GeoName= "' + state + r'" AND Line = "13"')
        for row in conn.engine.execute(sqlquery):
            datadict[y]["Services"] = str(row[0])
    return(jsonify(datadict))

@app.route("/countydata")
def county():
    slist = {}
    
    for rs in conn.engine.execute(r'select distinct "State" from acs2015_county_data'):
        s=str(rs[0])
        slist[s] = {}
        for rc in conn.engine.execute(r'select distinct "County" from acs2015_county_data where State="' + s + r'"'):
            c=str(rc[0])
            slist[s][c] = pd.read_sql_query(r'select * from acs2015_county_data where State="' + s + r'" and County="' + c + r'"',engine).T.to_dict()
    
    return(jsonify(slist))

if __name__ == "__main__":
    app.run(debug=True)