from app import app, db
from app.forms import MakeAppointmentForm, LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm
from flask import render_template, url_for, redirect, request, flash, abort
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Shop, Stock, Appointments
from werkzeug.urls import url_parse
from datetime import datetime


@app.route("/")
@app.route('/home')
def home():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("home.html", title="Home", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="Information")


@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact")


@app.route("/contact/social_media")
def social_media():
    return render_template("social_media.html", title="Contact")


@app.route("/contact/where_to_find")
def where_to_find():
    return render_template("where_to_find.html", title="Contact")


@app.route("/make_appointment", methods=['GET', 'POST'])
@login_required
def make_appointment():
    form = MakeAppointmentForm()
    if form.validate_on_submit():
        print(request.method)
        user = User.query.filter_by(username=current_user.username).first()
        print("OOF")
        user.total_num_app += 1
        print(request.form["date_time_form"])
        print("MOO")
        print(form.practice.data, form.appointment_type.data, request.form["date_time_form"])
        if form.appointment_type.data == "Eye_test":
            optomotrist = True
        else:
            optomotrist = False
        print(form.Date_time_input.data)
        appointment = Appointments(practice=form.practice.data, user_id=user.id, need_optom=optomotrist, date_time="2018-12-12 00:00")
        db.session.add(appointment)
        print(appointment)
        db.session.commit()
        # Put code here to add the appointment to the database
        print('First name :: {}\nLast name :: {}\nemail :: {}'.format(form.first_name.data, form.last_name.data, form.email.data))
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    dtnow = datetime.now()
    n=dtnow.minute
    if n < 30 and n != 0:
        n = 30
    elif n > 30:
        n = 0
    min_date_time = str(dtnow.date())+"T"+str(dtnow.hour)+":"+str(n)
    if len(str(dtnow.month + 3))==1:
        dtmaxmon = "0"+str(dtnow.month + 3)
    else:
        dtmaxmon = str(dtnow.month)
    if len(str(dtnow.day))==1:
        dtmaxday = "0"+str(dtnow.day)
    else:
        dtmaxday = str(dtnow.day)


    max_date_time = str(dtnow.year)+"-"+dtmaxmon+"-"+dtmaxday+"T"+str(dtnow.hour)+":"+str(n)
    print(min_date_time, max_date_time)
    return render_template("make_appointment.html", form=form, min_date_time=min_date_time, max_date_time=max_date_time, title="Appointment form")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name= form.last_name.data, username=form.username.data,
                    email=form.email.data, telephone_num=form.telephone_num.data, address1=form.address1.data,
                    address2=form.address2.data, town_city=form.town_city.data, postcode=form.postcode.data, total_num_app=0,
                    app_missed=0, total_mon_spen=0, perc_app_attend=0.0, mon_per_appoint=0.0, role=0)
        print(form.password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    if current_user.username != username:
            return abort(404)
    else:
        user = User.query.filter_by(username=username).first_or_404()
        posts = [
            {'author': user, 'body': 'Test post #1'},
            {'author': user, 'body': 'Test post #2'}
        ]
        return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/user/edit_profile/<username>', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    if current_user.username != username:
            return abort(404)
    else:
        form = EditProfileForm(current_user.username, current_user.email)
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            current_user.about_me = form.about_me.data
            current_user.telephone_num = form.telephone_num.data
            current_user.address1 = form.address1.data
            current_user.address2 = form.address2.data
            current_user.town_city = form.town_city.data
            current_user.postcode = form.postcode.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('edit_profile', username=current_user.username))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.first_name.data = current_user.first_name
            form.last_name.data = current_user.last_name
            form.email.data = current_user.email
            form.about_me.data = current_user.about_me
            form.telephone_num.data = current_user.telephone_num
            form.address1.data = current_user.address1
            form.address2.data = current_user.address2
            form.town_city.data = current_user.town_city
            form.postcode.data = current_user.postcode
        return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route("/user/edit_password/<username>", methods=["GET", "POST"])
@login_required
def change_password(username):
    if current_user.username != username:
            return abort(404)
    else:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=current_user.username).first()
            if user is None or not user.check_password(form.old_password.data):
                flash("Invalid password")
                return redirect(url_for('change_password', username=current_user.username))
            user.set_password(form.new_password.data)
            db.session.commit()
        return render_template("change_password.html", title="Change password", form= form)


@app.route("/Shop/<shop_filter>", methods=["GET", "POST"])
def shop_main(shop_filter):
    if shop_filter=="Male" or shop_filter=="Female":
        shop = Shop.query.filter_by(sex=shop_filter).all()
    # elif shop_filter == 1:#colour stuff
    #     for i in Stock.query.filter_by()
    else:
        shop = Shop.query.all()
    return render_template("shop_main.html", Title="Shop", shop=shop)


@app.route("/Shop_item/<shop_item_name>", methods=["GET","POST"])
def shop_item(shop_item_name):
    dic1={}
    item = Shop.query.filter_by(item_name=shop_item_name).first_or_404()
    stock = Stock.query.all()
    for i in stock:
        if i.item_id == item.id:
            dic1[i.colour] = i.quantity

    return render_template("shop_item.html", Title="Shop item", shop_item=item, stock=stock, stock_dic=dic1)


@app.route("/Shop/Cart/<username>", methods=["GET","POST"])
@login_required
def user_cart(username):
    return render_template("cart.html", Title="Cart", username=username)


@app.route("/Super_secret_page", methods=["GET", "POST"])
@login_required
def admin_page():
    if current_user.role < 1:
            return abort(404)
    else:
        return render_template("admin_page.html", Title="Admin")
