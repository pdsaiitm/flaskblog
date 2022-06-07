from select import select
from flask_mail import Mail
from flask import Flask
from flask  import  render_template,request,session,redirect
from datetime import datetime
from flask_sqlalchemy import  SQLAlchemy
import json
import math
from flask_ckeditor import CKEditor
from wtforms import StringField, SubmitField

with open("config.json","r") as p:
    param= json.load(p)["params"]

app = Flask(__name__)
ckeditor = CKEditor(app)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = param['user_email'],
    MAIL_PASSWORD = param['user_pass']
)
mail=Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = param["local_uri"]
db = SQLAlchemy(app)

class Contactus(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(14), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    msg = db.Column(db.String(120), nullable=False)

class Postinfo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(80), nullable=False)
    post_desc = db.Column(db.String(21), nullable=False)
    post_by = db.Column(db.String(120), nullable=False)
    post_date= db.Column(db.String(20), nullable=False)
    post_slug = db.Column(db.String(120), nullable=True)
    


@app.route("/dashboard", methods=[ "GET","POST"])
def login():
    error=''
    post =  Postinfo.query.filter_by().all()
    if "uname" in session and session['uname']==param['admin']:
        return render_template("dashboard.html", param=param,post=post)
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")
        if user==param["admin"] and pwd == param["pass"]:
            session["uname"]=user
            return render_template("dashboard.html",param=param,post=post)
        else:
            error='Invalid Credential'
            return render_template("login.html",param=param,error=error)
    else:
        return render_template("login.html",param=param,error=error)
@app.route("/logout")
def logout():
    error=''
    session["uname"]=None
    return render_template("login.html",param=param,error=error)


@app.route("/dashboard/delete/<int:sn>",methods=['GET','POST'])
def deletepost(sn):
    if "uname" in session and session['uname']==param['admin']: 
        Postinfo.query.filter_by(sno=sn).delete()
        db.session.commit()
        return redirect('/dashboard')  
    return render_template("login.html",param=param)


@app.route("/dashboard/edit/<int:sn>",methods=['GET','POST'])
def editpost(sn):
    if "uname" in session and session['uname']==param['admin']:     
        if request.method == "POST":
            title = request.form.get("ptitle")
            desc = request.form.get("ckeditor")
            by = request.form.get("pby")
            slug = request.form.get("pslug")
            print(sn)
            if sn == 0:
                entry = Postinfo(post_title=title,post_desc=desc,post_by=by,post_date=datetime.now(),post_slug=slug)
                db.session.add(entry)
                db.session.commit()
                print(sn)

            else:
                post = Postinfo.query.filter_by(sno=sn).first()
                post.post_title = title
                post.post_desc = desc
                post.post_by = by
                post.post_slug=slug
                db.session.commit()
            return redirect('/dashboard/edit/'+str(sn))
        post = Postinfo.query.filter_by(sno=sn).first()
        return render_template("editpost.html", param=param,post=post,sno=sn)
    return render_template("login.html",param=param)    


















@app.route("/")
def index():
    posts = Postinfo.query.filter_by().all()[::-1]
    last = math.ceil(len(posts)/int(param['no_of_post']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(param['no_of_post']):(page-1)*int(param['no_of_post'])+ int(param['no_of_post'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)

    return render_template("index.html",param=param,post=posts,prev=prev,next=next,size=last)


@app.route("/post/<int:p_slug>", methods = ['GET'])
def post_details(p_slug):
    post =  Postinfo.query.filter_by(sno=p_slug).first()
    return render_template("post.html" ,param=param,post=post)



@app.route("/about")
def about():
    return render_template("about.html" ,param=param)








@app.route("/contact" , methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contactus(name=name, phone = phone, msg = message,email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message("this is new message by"+name, sender=email, recipients =[param["user_email"]],body=message+"\n"+phone)
    return render_template("contact.html",param=param)

@app.route("/post")
def post():
    return render_template("post.html" ,param=param)

app.run()