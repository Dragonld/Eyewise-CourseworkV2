from app import app, db
from config import Config
from app.forms import MakeAppointmentForm, LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm,\
    AddMissedForm, AddMonForm, ChangeRoleForm, AddStockForm
from flask import render_template, url_for, redirect, request, flash, abort
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Shop, Stock, Appointments, Cart, Order
from werkzeug.urls import url_parse
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import threading
import spotipy
import time


class Thread_it:
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        token = SpotifyClientCredentials(client_id= Config.SPOTIFY_ID, client_secret=Config.SPOTIFY_SECRET)
        album_list =[]
        list_list=[]
        elevator_uri = 'spotify:artist:6aIG9cUZLDobp6suRM0vRL'
        spotify = spotipy.Spotify(client_credentials_manager=token)
        results = spotify.artist_top_tracks(elevator_uri)
        results = spotify.albums(["25GFQ04IGjmMnhW8O2Cz99", "47EIoHKC4M7RLL5pFWhfkd", "1ghDKd1sMvQ8k43e9kdelv", "15aKusaZoy3cGNXdelDNqJ"])
        previews=[]
        for album in results["albums"]:
            album_list.append(album)

        for album in results["albums"]:
            for thing in album["tracks"]["items"]:
                print(thing["preview_url"])
                previews.append(thing["preview_url"])


        # while True:
        #     print("Muffin")
        #     time.sleep(2)

@app.route("/", methods=["POST", "GET"])
def start_up():
    try:
        begin = Thread_it()
    except:
        return abort(500)
    return redirect("home")

@app.route('/home', methods=["GET", "POST"])
def home():
    begin = Thread_it()
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
        try:
            user = User.query.filter_by(email=form.email.data).first()
        except:
            flash("A user with your data cannot be found")
        print("OOF")
        user.total_num_app += 1
        date = str(form.year.data + "-" + form.month.data + "-" + form.day.data)
        time = str(form.hour.data + ":" + form.minute.data)
        date_time = date+ " " +time
        print(form.practice.data, form.appointment_type.data,date_time)
        if form.appointment_type.data == "eye_test":
            optomotrist = True
        else:
            optomotrist = False
        print(date_time, (int(form.hour.data)*60 + int(form.minute.data)), optomotrist)
        if int(form.year.data)<datetime.now().year\
                or int(form.month.data)<=datetime.now().month and int(form.year.data)==datetime.now().year\
                or int(form.day.data)<=datetime.now().day and int(form.month.data)==datetime.now().month and int(form.year.data)==datetime.now().year:
            flash("Appointments cannot be in the past")
            print("Attempt at past made")
            return redirect(url_for("make_appointment"))
        try:
            appointment = Appointments(practice=form.practice.data, appointment_type=form.appointment_type.data, user_id=user.id, need_optom=optomotrist, date_time=date_time)
            db.session.add(appointment)
            print(appointment)
            db.session.commit()
            flash("Appointment has been made")
        except:
            flash("The time slot you have requested is unavailable")
            return redirect(url_for("make_appointment"))
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.year.data = datetime.now().year
        form.month.data = datetime.now().month
    else:
        print(form.errors)
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
    return render_template("make_appointment.html", form=form, current_year=datetime.now().year, title="Appointment form")


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
                    app_missed=0, total_mon_spen=0, perc_app_attend=100.0, mon_per_appoint=0.0, role=0)
        print(form.password.data)
        #TODO remove above print
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        date = datetime.now().date()
        time = str(datetime.now().hour) + ":" + str(datetime.now().minute)
        new_cart = Cart(user_id=user.id, date_time_created=str(date) + " " + time, total_cost=0.0)
        db.session.add(new_cart)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    if current_user.username != username and current_user.role == 0 or current_user.is_anonymous:
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
    if current_user.username != username or current_user.is_anonymous:
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
    if current_user.username != username or current_user.is_anonymous:
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
    filter_list=[]
    colours=[]
    brands=[]
    ages=["Adult", "Kids"]
    for age in ages:
        filter_list.append(age)
    for item in Stock.query.all():
        if item.colour not in colours:
            colours.append(item.colour)
            filter_list.append(item.colour)
    for item in Shop.query.all():
        if item.brand not in brands:
            brands.append(item.brand)
            filter_list.append(item.brand)
    if shop_filter in ages:
        shop = Shop.query.filter_by(age=shop_filter).all()
    elif shop_filter in colours:
        shop = []
        for item in Stock.query.filter_by(colour=shop_filter).all():
            x = Shop.query.filter_by(id=item.item_id).first()
            shop.append(x)
    elif shop_filter in brands:
        shop = Shop.query.filter_by(brand=shop_filter).all()
    else:
        shop = Shop.query.all()
    return render_template("shop_main.html", Title="Shop", shop=shop, filter=shop_filter, filter_list=filter_list)


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
    if username != current_user.username or current_user.is_anonymous:
        return abort(404)
    user = User.query.filter_by(username=username).first()
    cart = Cart.query.filter_by(user_id=user.id).first()
    if request.method == "POST":
        item_id = request.form.getlist("item_id")[0]
        colour = request.form.getlist("colour")[0]
        shop = Shop.query.filter_by(id=item_id).first()
        stock = Stock.query.filter_by(item_id=shop.id, colour=colour).first()
        current_stock = stock.quantity
        if current_stock > 0:
            new_order = Order(cart_id=cart.id, shop_id=shop.id, colour=colour)
            stock.quantity = current_stock - 1
            db.session.add(new_order)
            db.session.commit()
            flash("Item has been added")
        else:
            flash("This product is out of stock")
            return redirect("shop_item.html", shop_item_name=shop.item_name)
    print("WADDLE")
    order_item_dic={}
    total_cost=0
    orders = Order.query.filter_by(cart_id=cart.id).all()
    for order in orders:
        x = Shop.query.filter_by(id=order.shop_id).first()
        x = x.id
        colour = order.colour
        if str(x)+str(colour) not in order_item_dic:
            order_item_dic[str(x)+str(colour)] = (Shop.query.filter_by(id=x).first(), 1, Shop.query.filter_by(id=x).first().price, order.colour)
        else:
            quantity = order_item_dic[str(x)+colour][1]
            quantity += 1
            order_item_dic[str(x)+colour] = (Shop.query.filter_by(id=x).first(), quantity, (Shop.query.filter_by(id=x).first().price*quantity), order.colour)
    for item in order_item_dic:
        total_cost += order_item_dic[item][0].price * order_item_dic[item][1]
    print("Waddle waddle")
    cart.total_cost = total_cost
    db.session.commit()
    return render_template("cart.html", Title="Cart", username=username, order_item_dic=order_item_dic, Shop=Shop, user=user, cart=cart, total_cost=total_cost)


@app.route("/Super_secret_page", methods=["GET", "POST"])
def admin_page():
    if current_user.role < 1 or current_user.is_anonymous:
            return abort(404)
    else:
        return render_template("admin_page.html", Title="Admin")


@app.route("/user_list", methods=["GET", "POST"])
@login_required
def user_list():
    if current_user.role == 0 or current_user.is_anonymous:
        return 404
    users = User.query.all()
    for user in users:
        if user.total_num_app != 0:
            user.perc_app_attend = 100-(user.app_missed/user.total_num_app)*100
            user.mon_per_appoint = (user.total_mon_spen/(user.total_num_app-user.app_missed))
        else:
            user.perc_app_attend = 100
            user.mon_per_appoint = 0
        db.session.commit()
    return render_template("user_list.html", users=users)


@app.route("/user/add_missed", methods=["GET", "POST"])
@login_required
def add_missed():
    if current_user.role == 0 or current_user.is_anonymous:
        return abort(404)
    form = AddMissedForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.app_missed += form.num_missed.data
        db.session.commit()
        flash("Change has been made")
    return render_template("app_missed.html", form=form)


@app.route("/user/add_mon", methods=["GET", "POST"])
@login_required
def add_mon():
    if current_user.role == 0 or current_user.is_anonymous:
        return abort(404)
    form = AddMonForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.total_mon_spen += form.mon_spent.data
        db.session.commit()
        flash("Change has been made")
    return render_template("add_mon.html", form=form)


@app.route("/my_appointments/<username>")
@login_required
def my_appointments(username):
    appointment_list=[]
    if current_user.username != username and current_user.role == 0 or current_user.is_anonymous:
            return abort(404)
    all_appointments = Appointments.query.all()
    if current_user.role == 0:
        user = User.query.filter_by(username=username).first()
        for appointment in all_appointments:
            if appointment.user_id == user.id:
                appointment_list.append([appointment, user])
    elif current_user.role < 3:
        for appointment in all_appointments:
            if current_user.role == 1:
                if appointment.practice == "Stourbridge":
                    user = User.query.filter_by(id=appointment.user_id).first()
                    appointment_list.append([appointment, user])
            elif current_user.role == 2:
                if appointment.practice == "Telford":
                    user = User.query.filter_by(id=appointment.user_id).first()
                    appointment_list.append([appointment, user])

    else:
        for appointment in all_appointments:
            user = User.query.filter_by(id=appointment.user_id).first()
            appointment_list.append([appointment, user])

    return render_template("my_appointments.html", title="Your appointments", appointments=appointment_list)


@app.route("/Whaaaa/esf7dgf76sgf<cart_id>aftaf6ats7f<item_id>as6fa7sahafa<colour>asygasifgasfga", methods=["POST", "GET"])
@login_required
def remove_item(item_id, colour, cart_id):
    cart = Cart.query.filter_by(id=cart_id).first()
    item = Shop.query.filter_by(id=item_id).first()
    stock = Stock.query.filter_by(item_id=item_id, colour=colour).first()
    order = Order.query.filter_by(cart_id=cart.id, shop_id=item.id, colour=colour).first()
    stock.quantity += 1
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for("user_cart", username=current_user.username))


@app.route("/Change_role", methods=["GET", "POST"])
@login_required
def change_role():
    if current_user.role < 3 or current_user.is_anonymous:
        return abort(404)
    form = ChangeRoleForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.role = form.new_role.data
        db.session.commit()
        flash(user.username + "is now role" + str(user.role))
    return render_template("change_role.html", title="change roll", form=form, )


@app.route("/Add_stock", methods=["GET", "POST"])
@login_required
def add_stock():
    if current_user.role < 3 or current_user.is_anonymous:
        return abort(404)
    form = AddStockForm()
    if form.validate_on_submit():
        shop = Shop.query.filter_by(item_name=form.item_name.data).first()
        stock = Stock.query.filter_by(item_id=shop.id, colour=form.colour.data).first()
        stock.quantity += form.stock.data
        db.session.commit()
    return render_template("add_stock.html", title="Add stock", form=form)

