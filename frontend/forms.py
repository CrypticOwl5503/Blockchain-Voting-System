"""
Form handling for the voting frontend.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    """Login form for voter authentication."""
    voter_id = StringField('Voter ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    """Registration form for new voters."""
    voter_id = StringField('Voter ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    otp = StringField('One-Time Registration Code', validators=[DataRequired()])
    submit = SubmitField('Register')

class VerificationForm(FlaskForm):
    """Form for two-factor authentication."""
    otp = StringField('One-Time Password', validators=[DataRequired()])
    submit = SubmitField('Verify')

class VoteForm(FlaskForm):
    """Form for casting a vote."""
    candidate = RadioField('Select a Candidate', validators=[DataRequired()])
    confirmation = HiddenField('Confirmation', validators=[DataRequired()])
    submit = SubmitField('Cast Vote')
