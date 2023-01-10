from flask import Flask, render_template, redirect, session, flash, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Word
from forms import SearchWord, UserForm, LoginForm
from sqlalchemy.exc import IntegrityError
import os
import re
import requests
import secret

BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


app = Flask(__name__)
app.app_context().push()


uri = os.environ.get('DATABASE_URL', 'postgresql:///dictionary')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY","helloworld1")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)



##############################################################################
# User signup/login/logout


@app.route('/register',methods=["GET","POST"])
def register():
    if "user_id" in session:
        return redirect ('/')
    
    else:
        form=UserForm()
        if form.validate_on_submit():
            first_name=form.first_name.data
            last_name=form.last_name.data
            password=form.password.data
            email=form.email.data
            new_user= User.register(email,password,first_name,last_name)
            db.session.add(new_user)
            try:
                db.session.commit()
                session['user_id']=new_user.id
            except IntegrityError:
                form.email.errors.append('This email has already been added')
                return render_template('register.html', form=form)
            
            
            return redirect('/')
        return render_template("register.html",form=form)



@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    if 'user_id' in session:
        return redirect('/')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.authenticate(form.email.data,
                                    form.password.data)

            if user:
                session['user_id']=user.id
                # flash(f"Hello, {user.first_name}!", "success")
                return redirect("/")

            flash("Invalid credentials.", 'danger')

        return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop("user_id")
    flash("Goodbye!", "info")
    return redirect('/login')

@app.route("/users/<int:user_id>")
def profile(user_id):
    user=User.query.get_or_404(int(user_id))
    return render_template('profile.html',user=user)



@app.route("/")
def home_page():
    
    return render_template('homepage.html')


@app.route("/api/get-word",methods=['POST'])
def search():
    # user_input = request.form.to_dict()['search'].lower() #if use wtforms instead of actual forms
    user_input = request.json['word']
    # print(user_input['word'])

    api_request = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/"+user_input)

    result = api_request.json()

    try:
        word=result[0]['word']
        audio=result[0]['phonetics'][0]['audio']
        pronunciation=result[0]['phonetics'][0].get('text','')
        definition=result[0]['meanings'][0]['definitions'][0]['definition']
        synonyms=result[0]['meanings'][0]['synonyms']
        grammer=result[0]['meanings'][0]['partOfSpeech']
        examples=result[0]['meanings'][0]['definitions'][0].get('example','')

        return jsonify({
            "word": {
                "word":word,
                "audio":audio,
                "pronunciation":pronunciation,
                "definitions":definition,
                "synonyms": synonyms,
                "grammer":grammer,
                "examples":examples,
            }
        })

    except:
        return result



