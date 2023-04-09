from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, DataRequired


class SearchWord(FlaskForm):
    search = StringField(
        "Enter Word",
        validators=[InputRequired()],
        render_kw={"placeholder": "Search English"},
    )


class AddSelection(FlaskForm):
    name = StringField("Selection Name", validators=[InputRequired()])


class UserForm(FlaskForm):
    first_name = StringField(
        "First Name", validators=[InputRequired(), Length(min=2, max=30)]
    )
    last_name = StringField(
        "Last Name", validators=[InputRequired(), Length(min=2, max=30)]
    )
    email = StringField("Email", validators=[InputRequired(), Length(min=5, max=50)])
    password = PasswordField("Password", validators=[InputRequired()])


class LoginForm(FlaskForm):
    """Login form."""

    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])


class AllSelection(FlaskForm):
    selection_list = SelectField("Select category to save:")
