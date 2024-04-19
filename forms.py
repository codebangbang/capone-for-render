from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length



class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    bio = TextAreaField('(Optional) Tell us about yourself')



class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = TextAreaField('(Optional) Tell us about yourself')
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])



# class BreweryForm(FlaskForm):
#     """Form for adding breweries."""

#     name = StringField('Brewery Name', validators=[DataRequired()])
#     street = StringField('Street', validators=[DataRequired()])
#     city = StringField('City', validators=[DataRequired()])
#     state = StringField('State', validators=[DataRequired()])
#     postal_code = StringField('Postal Code', validators=[DataRequired()])
#     website_url = StringField('Website', validators=[DataRequired()])
#     brewery_type = StringField('Brewery Type', validators=[DataRequired()])