from flask import Flask, render_template, redirect, session, flash, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Word, Selection, UserWord
from forms import SearchWord, UserForm, LoginForm, AddSelection, AllSelection
from sqlalchemy.exc import IntegrityError
import os
import re
import requests

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
    if 'user_id' not in session:
        return redirect('/')

    session.pop("user_id")
    flash("Goodbye!", "info")
    return redirect('/login')

@app.route("/<int:user_id>")
def profile(user_id):
    if "user_id" not in session:
        return redirect('/login')

    user=User.query.get_or_404(int(user_id))
    return render_template('profile.html',user=user)

##########################################################################################################
#words routes (GENERAL USE, ADD,)

@app.route("/",methods=["GET","POST"])
def home_page():
    form_word=SearchWord()
    form_selection=AllSelection()
    if session.get('user_id'):
        user = User.query.get_or_404(int(session["user_id"]))
        form_selection.selection_list.choices=[(x.id,x.name) for x in user.user_selection]
        form_selection.selection_list.choices.append(('New','New Category...'))
        
    

        

    if form_word.validate_on_submit():
        user_input=form_word.search.data
        print(user_input)
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
            answer={
                "word":word,
                "audio":audio,
                "definition":definition,
                "grammer":grammer,
                "pronunciation":pronunciation,
                "synonyms":synonyms,
                "examples":examples,
            }
            
            session['answer']=answer
            
        except:
            pass

        return render_template('home.html',form=form_word,answer=answer,form_selection=form_selection)


    

    return render_template('home.html',form=form_word,form_selection=form_selection)

@app.route('/<int:user_id>/card/new',methods=["POST"])
def add_word(user_id):
    if "user_id" not in session:
        return redirect('/login')

    card_selection = request.form['selection_list']
    if card_selection == 'New':
        return redirect (f"/{session['user_id']}/categories/add")

    new_word = Word(word=session['answer']['word'], 
    definition=session['answer']['definition'],
    grammer=session['answer']['grammer'],
    example=session['answer']['examples'],
    audio=session['answer']['audio'],
    pronunciation=session['answer']['pronunciation'],
    synonyms=session['answer']['synonyms'],
    selection_id=card_selection)
    db.session.add(new_word)
    db.session.commit()
    user_words =UserWord(user_id=user_id,word_id=new_word.id)
    db.session.add(user_words)
    db.session.commit()
    flash(f"{new_word.word} Added!", "success")
    return redirect ('/')

@app.route('/card/<int:word_id>/delete/',methods=["POST"])
def delete_word(word_id):
    if "user_id" not in session:
        return redirect('/login')

    word=Word.query.get_or_404(word_id)
    db.session.delete(word)
    flash(f"{word.word} Deleted!", "danger")
    db.session.commit()
    return redirect(f'/{session["user_id"]}/categories')
    





#########################################################################################################
#category routes (ALL, ADD, DELETE)

@app.route("/<int:user_id>/categories")
def all_categories(user_id):
    """Show all cards"""
    if "user_id" not in session:
        return redirect('/login')

    user=User.query.get_or_404(user_id)
    return render_template ('selection.html',user=user)

@app.route("/<int:user_id>/categories/add",methods=["GET","POST"])
def add_selection(user_id):
    if "user_id" not in session:
        return redirect('/login')

    form=AddSelection()
    if form.validate_on_submit():
        name=form.name.data
        new_selection=Selection(name=name,user_id=user_id)
        db.session.add(new_selection)
        db.session.commit()
        flash(f'{new_selection.name} added', "success")
        return redirect(f'/{user_id}/categories')

    return render_template('selectionform.html',form=form)

@app.route("/categories/<int:category_id>")
def category_info(category_id):
    if "user_id" not in session:
        return redirect('/login')

    category=Selection.query.get_or_404(category_id)

    return render_template ('category_info.html',category=category)


@app.route("/categories/<int:category_id>/delete",methods=["POST"])
def delete_selection(category_id):
    if "user_id" not in session:
        return redirect('/login')

    category = Selection.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    # flash(f'{category.name} Deleted', "danger")
    return redirect(f'/{session["user_id"]}/categories')

#################################################################################################################


