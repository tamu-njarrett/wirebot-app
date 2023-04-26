from datetime import datetime, time, timedelta
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from wirebot import db, bcrypt
from wirebot.models import User, Post, Status, RunTime
from wirebot.utils import run_wirebot, stop_wirebot
from wirebot.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from wirebot.users.utils import save_picture_user, send_reset_email, update_dashboard
import random, threading, calendar


users = Blueprint('users', __name__, template_folder='templates')

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:   
        return redirect(url_for('main.home'))    # if already logged in, register page sends to homepage
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))    # if already logged in, login page sends to homepage
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):  # check saved password vs. entered password
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))  # go to next page if one exists (account page before logging in)
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()                               # knows current_user is logged in
    return redirect(url_for('main.home'))       # sends to homepage after logout

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    # Updating account information via form on POST request
    if form.validate_on_submit():
        # Updating profile picture using save_picture()
        if form.picture.data:
            picture_file = save_picture_user(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated!', 'success')
        return redirect(url_for('users.account'))
    # Displaying current account information within form on GET request
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)  # pulling profile picture from static directory, within profile_pic folder getting current User image_file
    return render_template('account.html', title='Acount', image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


# Requesting token
@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with password reset instructions.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


# Once user has token from email
@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


# Checking status -> update_dashboard -> dashboard_values -> dashboard
@users.app_context_processor    # Using app_context_processor to inject values available even outside blueprint
def inject_load():
    connection = Status.query.filter_by(id=1).first().connection
    connection = 'Yes' if connection == True else 'No'

    row_num = Status.query.filter_by(id=1).first().row_num + 1

    status = ''
    if Status.query.filter_by(id=1).first().capturing == True:
        status = 'Capturing'
    elif Status.query.filter_by(id=1).first().rotating == True:
        status = 'Rotating'
    elif Status.query.filter_by(id=1).first().shifting == True:
        status = 'Shifting'
    elif Status.query.filter_by(id=1).first().finishing == True:
        status = 'Finishing'

    current_run_time = time()
    previous_run_time = RunTime.query.order_by(RunTime.id.desc()).first().run_time
    # Check if bot is finishing (returning home)
    if Status.query.filter_by(id=1).first().finishing:
        # Check if home operation has completed. If yes, then display total run time
        if RunTime.query.order_by(RunTime.id.desc()).first().run_time == None:
            current_run_time = datetime.now() - RunTime.query.order_by(RunTime.id.desc()).first().start_time
            total_seconds = int(current_run_time.total_seconds())
            hours, remainder = divmod(total_seconds,60*60)
            minutes, seconds = divmod(remainder,60)
            current_run_time = time(hours, minutes, seconds)    # Getting current run time while operating
            previous_run_time = 'Wirebot still running'
        else:
            run_time = RunTime.query.order_by(RunTime.id.desc()).first().run_time
    elif Status.query.filter_by(id=1).first().connection:
        current_run_time = datetime.now() - RunTime.query.order_by(RunTime.id.desc()).first().start_time
        total_seconds = int(current_run_time.total_seconds())
        hours, remainder = divmod(total_seconds,60*60)
        minutes, seconds = divmod(remainder,60)
        current_run_time = time(hours, minutes, seconds)    # Getting current run time while operating
    
    return {'connection': connection, 'status': status, 'row_num': row_num, 'current_run_time': current_run_time, 'previous_run_time': previous_run_time}


@users.before_app_first_request
def before_request():
    # Starts background thread for function we need to run before first client connects
    threading.Thread(target=update_dashboard, args=(current_app._get_current_object(), )).start()

# Dashboard route including html buttons that save to status file -> send websocket update
@users.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if request.form.get('run') == 'run':
            run_wirebot()
        elif request.form.get('stop') == 'stop':
            stop_wirebot()

    elif request.method == 'GET':
        return render_template('dashboard.html')


    return render_template('dashboard.html', title='Dashboard')


# @users.app_context_processor    # Using app_context_processor to inject values available even outside blueprint
# def inject_status():
#     load = [int(random.random() * 100) / 10 for _ in range(3)]
#     return {'load1': load[0], 'load5': load[1], 'load15': load[2]}

@users.route("/Wirebot_Status", methods=['GET'])
@login_required
def wirebot_status():
    
    return render_template('wirebot_status.html', title='Wirebot Status')


# Calendar display *** Incorporate time preset on specific days
@users.route("/Calendar", methods=['GET', 'POST'])
@login_required
def calendar_page():
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    calendar_current_month = calendar.month(currentYear, currentMonth)
    return render_template('calendar_page.html', title='Calendar', calendar_current_month=calendar_current_month)

@users.route("/Alerts", methods=['GET'])
@login_required
def alerts():

    return render_template('alerts.html', title='Alerts')
