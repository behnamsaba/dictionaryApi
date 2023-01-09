from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Word(db.Model):
    __tablename__ = 'words'
    def __repr__(self):

        """show info about word"""
        u = self
        return f'<word: id={u.id} word={u.word} definition={u.definition} grammer={u.grammer} example={u.example} audio={u.audio} pronunciation={u.pronunciation} synonym={u.synonym}>'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.Text, nullable=False)
    definition=db.Column(db.Text, nullable=False)
    grammer=db.Column(db.Text, nullable=False)
    example = db.Column(db.Text, nullable=False)
    audio=db.Column(db.Text,nullable=False)
    pronunciation=db.Column(db.Text)
    synonym=db.Column(db.Text,nullable=False)


    user_words = db.relationship('UserWord', backref="user", cascade="all,delete")


class User(db.Model):

    __tablename__ = 'users'
    def __repr__(self):
        """show info about user"""
        u = self
        return f'<user: id={u.id} email={u.email} first_name={u.first_name} last_name={u.last_name}>'
    
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    first_name= db.Column(db.Text, nullable=False)

    last_name =db.Column(db.Text, nullable=False)

    user_words = db.relationship('UserWord', backref="word", cascade="all,delete")

    @classmethod
    def register(cls, email, pwd, first_name, last_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(email=email, password=hashed_utf8, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


class UserWord(db.Model):
    """Mapping of a playlist to a song."""
    __tablename__ = 'users_words'

    def __repr__(self):
        """show info about users_words"""
        u = self
        return f'<users_words: user_id={u.user_id} word_id={u.word_id}>'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    word_id = db.Column(db.Integer,db.ForeignKey('words.id'),nullable=False)
    

