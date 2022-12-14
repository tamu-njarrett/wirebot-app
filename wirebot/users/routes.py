from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from wirebot import db, bcrypt
from wirebot.models import User, Post, Photo, Status, Location
from wirebot.utils import run_wirebot, stop_wirebot
from wirebot.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, DashboardForm
from wirebot.users.utils import save_picture_user, send_reset_email, update_dashboard
import random, threading


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


### Placeholder for real time values coming from Jetson TCP stream
@users.app_context_processor    # Using app_context_processor to inject values available even outside blueprint
def inject_load():
    #load = [int(random.random() * 100) / 10 for _ in range(3)]
    load = [int(random.random() * 100), int(random.randint(1,2)), int(random.random() * 1000)]
    # wirebot_position = int(random.random() * 30)
    # crop_row = int(random.uniform(0,2) * 2)
    # run_time = time.localtime() - start_time()
    return {'load1': load[0], 'load5': load[1], 'load15': load[2]}


@users.before_app_first_request
def before_request():
    # Starts background thread for function we need to run before first client connects
    threading.Thread(target=update_dashboard, args=(current_app._get_current_object(), )).start()

### Update request for user input on dashboard
@users.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    loc = Location(payload_loc=0,horizontal_loc=0)
    status = Status(connection=0,moving=0,picture_count=0)
    if "run" in request.form:
        pass; run_wirebot(status)
    if "stop" in request.form:
        pass; stop_wirebot(status)


    return render_template('dashboard.html', title='Dashboard')

# @users.app_context_processor    # Using app_context_processor to inject values available even outside blueprint
# def inject_status():
#     load = [int(random.random() * 100) / 10 for _ in range(3)]
#     return {'load1': load[0], 'load5': load[1], 'load15': load[2]}

@users.route("/Wirebot_Status", methods=['GET'])
@login_required
def wirebot_status():
    
    return render_template('wirebot_status.html', title='Wirebot Status')


@users.route("/Calendar", methods=['GET', 'POST'])
@login_required
def calendar():

    return render_template('calendar.html', title='Calendar')

@users.route("/Alerts", methods=['GET'])
@login_required
def alerts():

    return render_template('alerts.html', title='Alerts')

