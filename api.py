#!/usr/bin/python
# coding=utf8

from flask import Flask, make_response,url_for, render_template, request, redirect, session,Response
import os
#import numpy as np
import pathlib
from flask_sqlalchemy import SQLAlchemy #database interface
import pickle
from os import listdir
from os.path import isfile, join
import datetime
from os import path
import requests
import shutil
from subprocess import call
import string
import random
  
# importing the module
import json
  

#import time

def getuser():
    uname=session.get('user')
    if not uname: return None
    user=User.query.filter_by(username=uname).first()
    return user

def getuid():
    user=getuser()
    if not user: return -1
    return user.id

def getdate():
  currentDT = datetime.datetime.now()
  t=str(currentDT)
  tlist=t.split(" ")
  return tlist[0]

def lastid(obj):
      gid=obj.query.all()
      if not gid: return 0
      id=-1
      if len(gid)==0:return 0
      if gid is not None: id=gid[-1].id
      return id

def exists(path):
    if os.path.isfile (path) : return True
    else: return False
    
application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///csApp.db'
db = SQLAlchemy(application)

class User(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   status=db.Column(db.Integer)
   # 0, deactivated, 1 normal user, 2: admin user
   username = db.Column(db.String(), unique=True,index=True)
   email=db.Column(db.String())
   phone=db.Column(db.String())
   mobile=db.Column(db.String())
   password = db.Column(db.String())
   dept=db.Column(db.String(),index=True)
   join=db.Column(db.String())
   org=db.Column(db.String(),index=True)
   
   def __init__(self, username, password,dept="industry",phone="none",mobile="none",org="none",email="none"):
      self.username = username
      self.password = password
      self.email=email
      self.phone=phone
      self.mobile=mobile
      self.dept=dept
      self.status=1
      self.join=getdate()
      self.org=org
   
   def isAdmin(self):
        if self.status==2:
           return True
        else: return False
        
   def mydir(self):
       cwd=os.path.getcwd()
       dname=os.path.join(cwd,'static','users',str(self.id))
       return dname
  
class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(), index=True)
    name=db.Column(db.String())

    def __init__(self,id,name):
      self.sid = id
      self.name=name

class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(), index=True)
    name=db.Column(db.String())
    verified=db.Column(db.Boolean)
    
    def __init__(self,id,name,verified=False):
      self.sid = id
      self.name=name 
      self.verified=verified


class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(), index=True)
    created=db.Column(db.String())
    accepted=db.Column(db.Boolean)
    competition=db.Column(db.String())
    seller=db.Column(db.String())
    value=db.Column(db.Float)
    offered_capacity=db.Column(db.Float)
    def __init__(self,id,created,accepted,competition,seller,value,offered_capacity):
        self.sid = id
        self.created=created
        self.accepted=accepted
        self.competition=competition
        self.seller=seller
        self.value=value
        self.offered_capacity=offered_capacity

class Competition(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(), index=True)
    buyer= db.Column(db.String(), index=True)
    name= db.Column(db.String())
    openTime= db.Column(db.String())
    closed= db.Column(db.String())
    minimum_capacity=db.Column(db.Float)
    currency= db.Column(db.String())
    def __init__(self,id,buyer,name,openTime,closed,minimum_capacity,currency):
        self.sid = id
        self.buyer=buyer
        self.name=name
        self.open=openTime
        self.closed=closed
        self.minimum_capacity=minimum_capacity
        self.currency=currency

    
        
def loadBuyers():
    fname=os.path.join('static','data','buyers.json')
    with open(fname, 'r') as f:
        buyers = json.load(f)
    for buyer in buyers:
        id=buyer['id']
        name=buyer['name']
        # serach whether buyer exist, in case file updated
        # and need reload
        buyer0=Buyer.query.filter_by(sid=id).first()
        if buyer0: continue
        abuyer=Buyer(id,name)
        db.session.add(abuyer)
    db.session.commit()

# generate name with letters only
def generateName(N=20):
    # using random.choices()
    # generating random strings 
    res = ''.join(random.choices(string.ascii_uppercase +
        string.ascii_lowercase, k = N))
    return res

# generate name with letters+digits 
def generateMixStr(N=7):
    # using random.choices()
    # generating random strings 
    res = ''.join(random.choices(string.ascii_uppercase +
        string.ascii_lowercase+ string.digits, k = N))
    return res
   
   
def loadSellers():
    fname=os.path.join('static','data','sellers.json')
    with open(fname, 'r') as f:
        sellers = json.load(f)
    for seller  in sellers:
        id=seller['id']
        name=seller['name']
        verified=seller['verified']
        # serach whether seller exist, in case file updated
        # and need reload
        seller0=Seller.query.filter_by(sid=id).first()
        if seller0: continue
        aseller=Seller(id,name,verified)
        db.session.add(aseller)
    db.session.commit()
    
def loadBids():
    fname=os.path.join('static','data','bids.json')
    with open(fname, 'r') as f:
        bids = json.load(f)
    for bid  in bids:
        id=bid['id']
        created=bid['created']
        accepted=bid['accepted']
        competition=bid['competition']
        seller=bid['seller']
        value=bid['value']
        offered_capacity=bid['offered_capacity']
        # serach whether bid exist, in case file updated
        # and need reload
        bid0=Bid.query.filter_by(sid=id).first()
        if bid0: continue
        abid=Bid(id,created,accepted,competition,seller,value,offered_capacity)
        db.session.add(abid)
    db.session.commit()  
 
def loadCompetitions():
    fname=os.path.join('static','data','competitions.json')
    with open(fname, 'r') as f:
        competitions = json.load(f)
    for competition in competitions:
        id=competition['id']
        buyer=competition['buyer']
        name=competition['name']
        openTime=competition['open']
        closed=competition['closed']
        minimum_capacity=competition['minimum_capacity']
        currency=competition['currency']
        # serach whether bid exist, in case file updated
        # and need reload
        comp0=Competition.query.filter_by(sid=id).first()
        if comp0: continue
        #(self,id,buyer,name,open,closed,minimum_capacity,currency)
        aComp=Competition(id,buyer,name,openTime,closed,minimum_capacity,currency)
        db.session.add(aComp)
    db.session.commit()  

def initServer():
    loadBuyers()
    loadSellers()
    loadBids()
    loadCompetitions()
    
        
welcome='Welcome to use Contest-selling: cloud-based sell & buy platform'
info={'topic':'none','msg':welcome,'user':'none'}
Info={}
#initServer()   


application.debug = False
db.create_all()
application.secret_key = "csapp-2021-05-18@*+U"

@application.route('/', methods=['GET', 'POST'])
def home():
    id=getuid()
    if id not in Info.keys():
        Info[id]={}
    info=Info[id]
    info['topic']='none'
    info['msg']=welcome
    if not session.get('logged_in'):
        return render_template('index.html',info=info)
    else:
        if request.method == 'POST':
            username = getname(request.form['username'])
            return render_template('index.html')
    return render_template('index.html',info=info)


@application.route('/putCompetition', methods=['GET', 'POST'])
def putCompetition():
    user=getuser()
    id=0   
    if user: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    
    info['topic']="putCompetition"
    info['msg']='Put a competition as a buyer of product or service'
    
    if not user:
        info['msg']="Error put a competition: you need to login to your account first"
        return render_template('index.html',info=info)    
    
    if request.method == 'GET':
        return render_template('index.html',info=info)
    
    button=request.form.get('button')
    if button=="Cancel":
        info['topic']='none'
        info['msg']="Put competition operation cancelled"
        return render_template('index.html',info=info)    
    sid =generateMixStr()
    buyer=request.form.get('acName')
    info['acName']=buyer
    abuyer=Buyer.query.filter_by(sid=buyer)
    if not abuyer:
        info['msg']="Error put a competition: buyer account name not found"
        return render_template('index.html',info=info)    
        
    name=generateName()
    openTime=request.form.get('openTime')
    info['openTime']=openTime
    
    closeTime=request.form.get('closeTime')
    info['closeTime']=closeTime
   
    sminimum_capacity=request.form.get('minimum_capacity')
    info['minimum_capacity']=sminimum_capacity
    
    try:
        minimum_capacity=float(sminimum_capacity)
    except:
        info['msg']="Error put a competition: minimum capacity must be a number"
        return render_template('index.html',info=info) 
        
    currency=request.form.get('currency') 
    info['currency']=currency 
    #(self,id,buyer,name,openTime,closed,minimum_capacity,currency)
    comp=Competition(sid,buyer,name,openTime,closeTime,minimum_capacity,currency)
    db.session.add(comp)
    db.session.commit()
    info['msg']="Advertised competition stored into database"
    return render_template('index.html',info=info)

"""
A bid is **successful** if the following is true:

 - its `offered_capacity` is equal to or greater than than the competition's
   `minimum_capacity` #done
 - its `accepted` state is true # done
 - its associated `seller`'s `verified` state is true # done
 - it was created within the associated competition's `open` and `closed` dates, #done

"""

def compareDates(d1,d2):
    #d1>d2, return 1, d1<d2: return -1, d1==d2: return 0
    ld1=d1.split(' ')
    ld2=d1.split(' ')
    if (ld1[0]>ld2[0]): return 1
    elif ld1[0]<ld2[0]: return -1
    # d1[0]==d2[0]
    if ld1[1]>ld2[1]: return 1
    if ld1[1]<ld2[1]: return -1
    return 0
    
def isBidSuccess(bid,aCompetition):
    if not bid.accepted:
        return False
    seller=bid.seller
    aSeller=Seller.query.filter_by(sid=seller).first()
    if not aSeller: return False
    if not aSeller.verified: 
        return False    
    capacity=bid.offered_capacity
    if capacity<aCompetition.minimum_capacity: return False
    d1= bid.created
    d20=aCompetition.openTime
    if compareDates(d1,d20)==-1: return False #bid too early
    d21=aCompetition.closed
    if compareDates(d1,d21)==1: return False #bid too late
    return True
    
def timeNow():
    now = datetime.datetime.now()
    stime=str(now.strftime("%Y-%m-%d %H:%M:%S"))
    return stime
 
@application.route('/allCompetitions', methods=['GET', 'POST'])
def allCompetitions():
    # List all competitions regardless whether or not have a successful bid
    user=getuser()
    id=0   
    if user: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    
    info['topic']="allCompetitions"
    info['msg']='List all competitions with its name'
    
    if not user:
        info['msg']="Error list competitions: you need to login to your account first"
        return render_template('index.html',info=info)    
    
    comps=Competition.query.all()
    nbids=[]
    for comp in comps:
        sid=comp.sid
        #search all bids attached to this competition
        bids=Bid.query.filter_by(competition=sid).all()
        nbids.append(len(bids))
        
    compInfo=[['index','buyer','Number of bids','Name']]
    for i in range(len(comps)):
        nbid=nbids[i]
        comp=comps[i]
        slist=[comp.id,comp.buyer,nbid,comp.name]
        compInfo.append(slist)
    info['compInfo']=compInfo
    info['msg']='List of all competitions'
    return render_template('index.html',info=info)  
    
           
@application.route('/searchCompetition', methods=['GET', 'POST'])
def searchCompetition():
    #search competition which has a seccessful bids
    user=getuser()
    id=0   
    if user: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    
    info['topic']="searchCompetition"
    info['msg']='Search competitions which has a successful bid'
    
    if not user:
        info['msg']="Error search competition: you need to login to your account first"
        return render_template('index.html',info=info)    
    
    comps=Competition.query.all()
    #print('number of comps',len(comps))
          
    lcomps=[]
    for comp in comps:
        sid=comp.sid
        #search all bids attached to this competition
        bids=Bid.query.filter_by(competition=sid).all()
        if len(bids)==0: continue
        for bid in bids:
            success=isBidSuccess(bid,comp)
            
            if success:
                lcomps.append(comp)
                break
    compInfo=[['index','id','buyer','open','closed',"minimum_capacity","currency"]]
    for comp in lcomps:
        slist=[comp.id,comp.sid,comp.buyer,comp.openTime,comp.closed,comp.minimum_capacity,comp.currency]
        compInfo.append(slist)
    info['compInfo']=compInfo
    info['msg']='List of competitions with at least 1 successful bid'
    return render_template('index.html',info=info)  
    
@application.route('/putBid', methods=['GET', 'POST'])
def putBid():
    user=getuser()
    id=0   
    if user: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    
    info['topic']="putBid"
    info['msg']='Put a bid as a seller of product or service'
    
    if not user:
        info['msg']="Error put a bid: you need to login to your account first"
        return render_template('index.html',info=info)    
    
    if request.method == 'GET':
        return render_template('index.html',info=info)
    
    button=request.form.get('button')
    if button=="Cancel":
        info['topic']='none'
        info['msg']="Put bid operation cancelled"
        return render_template('index.html',info=info)    
    
    sid =generateMixStr()
    seller=request.form.get('acName')
    
    info['acName']=seller
    aseller=Seller.query.filter_by(sid=seller)
    if not aseller:
        info['msg']="Error put a bid: seller account name not found"
        return render_template('index.html',info=info)    
    
    created = timeNow() 
    accepted=False
    competition=request.form.get('competition')
    info['competition']=competition
   
    svalue=request.form.get('value')
    info['value']=svalue
    
    try:
        value=float(svalue)
    except:
        info['msg']="Error put a bid: bid value must be a number"
        return render_template('index.html',info=info) 
        
    soffered_capacity=request.form.get('offered_capacity') 
    info['offered_capacity']= soffered_capacity
    try:
        offered_capacity=float(soffered_capacity)
    except:
        info['msg']="Error put a bid: offered_capacity must be a number"
        return render_template('index.html',info=info) 
                
    #(self,id,created,accepted,competition,seller,value,offered_capacity)
    abid=Bid(sid,created,accepted,competition,seller,value,offered_capacity)
    db.session.add(abid)
    db.session.commit()
    info['msg']="Advertised bid stored into database"
    return render_template('index.html',info=info)

@application.route('/acceptBid' , methods=['GET', 'POST'])
def acceptBid():
    user=getuser()
    id=0   
    if user: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    
    info['topic']="acceptBid"
    info['msg']='Change bid status to accepted, you need to be system admin to do this operation'
    
    if not user:
        info['msg']="Error change bid  status: you need to login to your account first"
        return render_template('index.html',info=info)    
    if user.status<2:
        info['msg']="Error change bid status: you need to be an admin"
        return render_template('index.html',info=info)    
    bids=Bid.query.filter_by(accepted=False).all()
    if len(bids)==0:
        info['msg']="Error change bid status: no non-accepted bids in database"
        return render_template('index.html',info=info)    
    lbid=[['id','Seller','Creation Time','Competition','value','offered_capacity','Acceptance status']]
    for bid in bids:
        slist=[bid.id, bid.seller,bid.created,bid.competition,bid.value,bid.offered_capacity,bid.accepted]
        lbid.append(slist)
   
    info['bids']= lbid 
    
    if request.method == 'GET':
        return render_template('index.html',info=info)
   
    button=request.form.get('button')
    if button=="Cancel":
        info['topic']='none'
        info['msg']="Accept bid operation cancelled"
        return render_template('index.html',info=info)        
    
    sid=request.form.get('sid')
    info['sid']=sid
    
    if not sid:
        msg='Error change bid status: bid id not specified'
        info['msg']=msg
        return render_template('index.html',info=info) 
    try: id=int(sid)
    except Exception as e:
        msg='Error change bid status, error message is:'+str(e)
        info['msg']=msg
        return render_template('index.html',info=info)    
    abid=Bid.query.filter_by(id=id).first()
    if not abid:
        msg='Error change bid status: incorrect bid id'
        info['msg']=msg
        return render_template('index.html',info=info)     
    abid.accepted=True
    db.session.commit() 
    msg='Bid with ID '+sid+' is accepted'
    info['msg']=msg  
    return render_template('index.html',info=info)   
    
@application.route('/verifySeller' , methods=['GET', 'POST'])
def verifySeller():
    user=getuser()
    id=0   
    if user: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    
    info['topic']="verifySeller"
    info['msg']='Verify seller status, you need to be system admin to do this operation'
    
    if not user:
        info['msg']="Error verify seller status: you need to login to your account first"
        return render_template('index.html',info=info)    
    if user.status<2:
        info['msg']="Error verify seller status: you need to be an admin"
        return render_template('index.html',info=info)   
    sellers=Seller.query.filter_by(verified=False).all()
    if len(sellers)==0:
        info['msg']="Error verify seller status: no unverified sellers in database"
        return render_template('index.html',info=info)    
    lseller=[['id','account name','Verification status']]
    for seller in sellers:
        slist=[seller.id, seller.sid,seller.verified]
        lseller.append(slist)
   
    info['sellers']= lseller  
    
    if request.method == 'GET':
        return render_template('index.html',info=info)
   
    button=request.form.get('button')
    if button=="Cancel":
        info['topic']='none'
        info['msg']="Verify seller operation cancelled"
        return render_template('index.html',info=info)        
    
    sid=request.form.get('sid')
    info['sid']=sid
    
    if not sid:
        msg='Error verify seller: seller id not specified'
        info['msg']=msg
        return render_template('index.html',info=info) 
    try: id=int(sid)
    except Exception as e:
        msg='Error verify seller, error message is:'+str(e)
        info['msg']=msg
        return render_template('index.html',info=info)    
    seller=Seller.query.filter_by(id=id).first()
    if not seller:
        msg='Error verify seller, seller id incorrect'
        info['msg']=msg
        return render_template('index.html',info=info)     
    seller.verified=True
    db.session.commit() 
    msg='Seller with ID '+sid+' is verified'
    info['msg']=msg  
    return render_template('index.html',info=info)   
    
@application.route('/getAdminStatus' , methods=['GET', 'POST'])
def getAdminStatus():
    
    user=getuser()
    id=0   
    if user: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    
    info['topic']='getAdminStatus'
    info['msg']="Register as an admin to carry out corresponding operations"
    if not user:
        info['msg']="Error register as admin: you need to login to your account first"
        return render_template('index.html',info=info)    
    if request.method == 'GET':
        return render_template('index.html',info=info)
    
    button=request.form.get('button')
    if button=="Cancel":
        info['topic']='none'
        info['msg']="Registration as an admin operation cancelled"
        return render_template('index.html',info=info)    
    if button=="Apply":
        passwd=request.form.get('passwd') 
        
        if passwd != adminPassword:
            info['msg']="Incorrect password"
            return render_template('index.html',info=info)   
        user.status=2
        db.session.commit()
        info['msg']="Your status has been upgraded to Admin"
        return render_template('index.html',info=info) 

@application.route('/buyerRegist' , methods=['GET', 'POST'])
def buyerRegist():
    id=getuid()
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    info['topic']='buyerRegist'
    info['msg']="Register as a buyer to buy products or services by bidding"
    if request.method == 'GET':
        return render_template('index.html',info=info)
    
    button=request.form.get('button')
    if button=="Cancel":
        info['topic']='none'
        info['msg']="Registration as a buyer operation cancelled"
        return render_template('index.html',info=info)    
    acName=request.form.get('acName')
    info['acName']=acName
    if not acName:
        info['msg']="Please specify an account name"
        return render_template('index.html',info=info)    
    
    buyer0=Buyer.query.filter_by(sid=acName).first()
    if buyer0:
        info['msg']="Error register as a buyer: account name already in use"
        return render_template('index.html',info=info) 
    name=generateName()
    abuyer=Buyer(acName,name)
    db.session.add(abuyer)
    db.session.commit()
    info['msg']="Registration as a buyer succeeded"
    return render_template('index.html',info=info)    

@application.route('/sellerRegist' , methods=['GET', 'POST'])
def sellerRegist():
    id=getuid()
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    info['topic']='sellerRegist'
    info['msg']="Register as a seller to sell products or services by bidding"
    if request.method == 'GET':
        return render_template('index.html',info=info)
    
    button=request.form.get('button')
    if button=="Cancel":
        info['topic']='none'
        info['msg']="Registration as a seller operation cancelled"
        return render_template('index.html',info=info)    
    acName=request.form.get('acName')
    info['acName']=acName
    if not acName:
        info['msg']="Please specify an account name"
        return render_template('index.html',info=info)    
    
    seller0=Seller.query.filter_by(sid=acName).first()
    if seller0:
        info['msg']="Error register as a seller: account name already in use"
        return render_template('index.html',info=info) 
    name=generateName()
    aseller=Seller(acName,name)
    db.session.add(aseller)
    db.session.commit()
    info['msg']="Registration as a seller succeeded"
    return render_template('index.html',info=info)    

           
@application.route('/regist' , methods=['GET', 'POST'])
def regist():
    id=getuid()
    if id not in Info.keys():Info[id]={}
    info=Info[id]
    if id>=0:
        info['msg']="You already registered. Please choose another service"
        info['topic']='none'
        return render_template('index.html',info=info)
    info['topic']='regist'
    info['msg']=welcome
    if request.method == 'GET':
        return render_template('index.html',info=info)
    button=request.form.get('button')
    if button=="Cancel":
        info['topic']='none'
        info['msg']="Registration operation cancelled"
        return render_template('index.html',info=info)
    wno=request.form['username']
    if ' ' in wno:
        info['msg']='Error:  username must not contain spaces'
        return render_template('index.html',info=info)
   
    email=request.form.get('email')
    phone=request.form.get('phone')
    mobile=request.form.get('mobile')
    org="public"
    dept="individual"
        
    data=User.query.filter_by(username=wno).first()
    if data is not None:
        f="Error: user name already in use. Please enter another:"
        info['msg']=f
        return render_template('index.html',info=info)
    if len(email)>=6:
        data=User.query.filter_by(email=email).first()
        if data is not None:
            f="Error: email address already in use. Please enter another"
            info['msg']=f
            return render_template('index.html',info=info)    
       
    passwd=request.form['password']
    passwd2=request.form['password2']
        
    if passwd !=passwd2:
        f="Error: password and repeated password must be the same"
        info['msg']=f
        return render_template('index.html',info=info)
    if (len(passwd)<6):
        f="Error: password length must be >= 6"
        info['msg']=f
        return render_template('index.html',info=info)
    
    new_user = User(username=wno, password=passwd,dept=dept,org=org,email=email,phone=phone,
    mobile=mobile)
    db.session.add(new_user)
    db.session.commit()
    id=lastid(User)
    
    dname=os.path.join('static','users',str(id)) 
   
    pathlib.Path(dname).mkdir(parents=True, exist_ok=True)
    
    session['logged_in'] = True
    session['user'] = wno
    session['isadmin'] = False
    f="Welcome "+wno+" to use CSApp"
    info['msg']=f
    info['topic']='about'
    return render_template('index.html',info=info)

@application.route('/logout' , methods=['GET', 'POST'])
def logout():
    user=getuser()
    if not user: id=0        
    else: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]    
    if not session['logged_in'] :
        info['msg']='Logout Error：you are not logged in'
        info['topic']='login'
        return render_template('index.html',info=info)   
    f="You are logged out"
    session['logged_in'] = False
    session['user'] =None
    session['isadmin'] = False
    info['msg']=f  
    info['topic']='none'
    return render_template('index.html',info=info)         

@application.route('/updateServer', methods=['GET', 'POST']) 
def updateServer():
    user=getuser()
    if not user: id=0        
    else: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]  
    
    info['msg']="Update server status, you need to be system Admin to carry out this operation"
    info['topic']='updateServer'
    if request.method == 'GET':
        return render_template('index.html',info=info)
    button= request.form.get('button')   
    if button=="Cancel":
        info['topic']='none'
        info['msg']="Update server action cancelled"
        return render_template('index.html',info=info)    
    if button=="Apply":
        passwd=request.form.get('passwd') 
        
        if passwd != adminPassword:
            info['msg']="Incorrect password"
            return render_template('index.html',info=info)   
        initServer()
        info['msg']="Server database updated"
        return render_template('index.html',info=info) 
               
    return render_template('index.html',info=info) 
      
@application.route('/user_login' , methods=['GET', 'POST']) 
def user_login():
    user=getuser()
    if not user: id=0        
    else: id=user.id
    if id not in Info.keys():Info[id]={}
    info=Info[id]    
    info['msg']=welcome
    info['topic']='user_login'
    
    if user:
        info['msg']='You already logged in'
        info['topic']='none'
        return render_template('index.html',info=info)
    
    if request.method == 'GET':
        return render_template('index.html',info=info)
    
    name = request.form['username']
    passw = request.form['password']
    user=User.query.filter_by(username=name).first()
    
    try:
        data = User.query.filter_by(username=name, password=passw).first()
        fname = User.query.filter_by(username=name).first()
        if fname is None:
            f="Error: user name not exists. Please register first"
            info['msg']=f
            return render_template('index.html',info=info)
        if data is not None:
            id=data.id
            sid=str(id)
            session['logged_in'] = True
            session['isadmin'] = False
            session['user'] = name
            session['uid']=sid
            session['group'] = False
            f="Welcome "+name+" to use WebDAT"
            info['msg']=f
            info['topic']='none'
            return render_template('index.html',info=info)
        else:
            f="Error login: incorrect password"
            info['msg']=f
            return render_template('index.html',info=info)
    except:
        f="Error: incorrect password"
        info['msg']=f
        return render_template('index.html',info=info)
    info['topic']='none'   
    return render_template('index.html',info=info)
 
adminPassword='aSk3pTW327'    
if __name__ == '__main__':
   
   application.run(host='0.0.0.0')


