from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Word
from forms import SearchWord, UserForm, LoginForm
from sqlalchemy.exc import IntegrityError
import os
import re
import requests
import secret

BASE_URL = "https://od-api.oxforddictionaries.com:443/api/v2/entries/en-us/"


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
    form=SearchWord()
    return render_template('homepage.html')


@app.route("/api/get-word",methods=['POST'])
def search():
    user_input = request.form.to_dict()['search'].lower()

    print(BASE_URL+user_input)
    api_request = requests.get(BASE_URL+user_input ,headers={"app_id": secret.app_id, "app_key": secret.app_key})
    result = api_request.json()

    


    # print(res['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][1]['audioFile'])

    
    return redirect('/')


