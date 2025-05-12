"""
Web routes for the blockchain voting frontend.
"""
from flask import render_template, url_for, flash, redirect, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from frontend.app import app, login_manager
from frontend.forms import LoginForm, RegisterForm, VerificationForm, VoteForm
from api.routes import get_election_info, register_voter, verify_voter, cast_vote, get_results
import json
import hashlib
import secrets

# Mock user model for login management
class User:
    def __init__(self, id):
        self.id = id
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        
    def get_id(self):
        return self.id

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    """Home page with election information."""
    election_info = get_election_info()
    return render_template('index.html', election=election_info)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Voter registration page."""
    form = RegisterForm()
    
    if form.validate_on_submit():
        voter_id = form.voter_id.data
        password = form.password.data
        otp = form.otp.data
        
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Register the voter via API
        success, message = register_voter(voter_id, password_hash, otp)
        
        if success:
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Registration failed: {message}', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Voter login page."""
    form = LoginForm()
    
    if form.validate_on_submit():
        voter_id = form.voter_id.data
        password = form.password.data
        
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Verify login credentials via API
        success, result = verify_voter(voter_id, password_hash)
        
        if success:
            # Store OTP in session for verification
            session['otp'] = result.get('otp')
            session['voter_id'] = voter_id
             
            return redirect(url_for('verify'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """Two-factor authentication verification page."""
    if 'voter_id' not in session or 'otp' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
        
    form = VerificationForm()
    
    if form.validate_on_submit():
        entered_otp = form.otp.data
        expected_otp = session['otp']
        
        if entered_otp == expected_otp:
            # Log in the user
            user = User(session['voter_id'])
            login_user(user)
            
            # Clear OTP from session
            session.pop('otp', None)
            
            flash('Verification successful!', 'success')
            return redirect(url_for('vote'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    
    return render_template('verify.html', form=form)

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    """Voting page."""
    # Get election info and candidates
    election_info = get_election_info()
    
    if election_info['state'] != 'VOTING':
        flash('Voting is not currently open.', 'warning')
        return redirect(url_for('index'))
    
    # Create form with dynamic candidate choices
    form = VoteForm()
    form.candidate.choices = [(c['name'], c['name']) for c in election_info['candidates']]
    
    if form.validate_on_submit():
        # Get selected candidate
        candidate = form.candidate.data
        voter_id = current_user.id
        
        # Cast vote via API
        success, message = cast_vote(voter_id, candidate)
        
        if success:
            flash('Your vote has been cast successfully!', 'success')
            return redirect(url_for('thank_you'))
        else:
            flash(f'Error casting vote: {message}', 'danger')
    
    return render_template('vote.html', form=form, election=election_info)

@app.route('/thank-you')
@login_required
def thank_you():
   
    return render_template('thank_you.html')

@app.route('/results')
def results():
    """Election results page."""
    election_info = get_election_info()
    
    if election_info['state'] not in ['TALLYING', 'CLOSED']:
        flash('Results are not available yet.', 'info')
        return redirect(url_for('index'))
    
    success, results_data = get_results()
    
    if not success:
        flash('Error retrieving results.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('results.html', election=election_info, results=results_data)

@app.route('/logout')
def logout():
    """Logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
