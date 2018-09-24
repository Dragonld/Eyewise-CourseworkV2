from app import app, db
from config import Config
from app.forms import MakeAppointmentForm, LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm,\
    AddMissedForm, AddMonForm, ChangeRoleForm, AddStockForm, OptomForm, HelpForm, AddShopForm, EmailForm, LostPassForm
from flask import render_template, url_for, redirect, request, flash, abort
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Shop, Stock, Appointments, Cart, Order, OptomThere, ArchiveApp, QuestAns
from werkzeug.urls import url_parse
from datetime import datetime
import threading
import hashlib
import string
import random
import smtplib
import json

#TODO NE deletes year old appointments
#TODO NE add a cancel appointment option
#TODO NE make the website show charge fees in the appointment has been made flash
#TODO NE create a logo
#TODO - Ambitious - add search to shop if really wanted
#TODO questions
#TODO NE Add an email sending thing to remind patients of appointments
#TODO NE Add data to the information pages.
#TODO Half done Add an image upload to shop item adding
#TODO NE Google charts to compare how much bought of each colour, brand and age.
#TODO Add reset password secure thing
#TODO add auto restock email



quest_answ = QuestAns.query.all()


class Thread_it:
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        for appointment in Appointments.query.all():
            
            if int(appointment.date_time[:4]) == datetime.now().year:
                if int(appointment.date_time[5:7]) == datetime.now().month:
                    if int(appointment.date_time[8:10]) == datetime.now().day-1:
                        archapp = ArchiveApp(user_id=appointment.user_id, practice=appointment.practice,
                                             date_time=appointment.date_time,
                                             appointment_type=appointment.appointment_type)
                        db.session.delete(appointment)
                        db.session.add(archapp)
                        db.session.commit()
                elif int(appointment.date_time[5:7]) == datetime.now().month+1 and datetime.now().day == 1:
                        archapp = ArchiveApp(user_id=appointment.user_id, practice=appointment.practice,
                                             date_time=appointment.date_time,
                                             appointment_type=appointment.appointment_type)
                        db.session.delete(appointment)
                        db.session.add(archapp)
                        db.session.commit()
            elif int(appointment.date_time[:4]) == datetime.now().year-1 and (datetime.now().month and datetime.now().day) == 1:
                    archapp = ArchiveApp(user_id=appointment.user_id, practice=appointment.practice,
                                         date_time=appointment.date_time,
                                         appointment_type=appointment.appointment_type)
                    db.session.delete(appointment)
                    db.session.add(archapp)
                    db.session.commit()
                #TODO NE Check that ARCHIVE DAY OLD APPOINTMENTS NOT YEAR OLD ONES



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
    return render_template("home.html", title="Home", posts=posts, quest_answ=quest_answ)


@app.route("/about")
def about():
    return render_template("about.html", title="Information", quest_answ=quest_answ)


@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact", quest_answ=quest_answ)


@app.route("/contact/social_media")
def social_media():
    return render_template("social_media.html", title="Contact", quest_answ=quest_answ)


@app.route("/contact/where_to_find")
def where_to_find():
    return render_template("where_to_find.html", title="Contact" , quest_answ=quest_answ)


@app.route("/make_appointment", methods=['GET', 'POST'])
@login_required
def make_appointment():
    form = MakeAppointmentForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
        except:
            flash("A user with your data cannot be found")
            return redirect(url_for("make_appointment"))
        appointments = Appointments.query.filter_by(user_id=user.id).all()
        if len(appointments) >= 3:
            flash("You can ony have three appointments at one time")
            return redirect(url_for("make_appointment"))
        user.total_num_app += 1
        if len(form.month.data) == 1:
            month = "0" + str(form.month.data)
        else:
            month=form.month.data
        if len(form.day.data) == 1:
            day = "0" + form.day.data
        else:
            day=form.day.data
        date = str(str(form.year.data) + "-" + month+ "-" + day)
        time = str(form.hour.data + ":" + form.minute.data)
        date_time = date + " " + time
        if form.appointment_type.data == "Eye test":
            optometrist = True
        else:
            optometrist = False
        if int(form.year.data)<datetime.now().year\
                or int(form.month.data)<datetime.now().month and int(form.year.data)==datetime.now().year\
                or int(form.day.data)<=datetime.now().day and int(form.month.data)==datetime.now().month and int(form.year.data)==datetime.now().year:
            flash("Appointments cannot be in the past")
            return redirect(url_for("make_appointment"))
        if form.month.data=="2" and form.day.data=="30":
            flash("February does not have 30 days")
            return redirect(url_for("make_appointment"))
        if form.month.data==("2" or "4" or "6" or "9" or "11") and form.day.data == "31":
            flash("Your selected month does not contain 31 days")
            return redirect(url_for("make_appointment"))
        if int(form.year.data)%4 != 0 and form.month.data == "2" and form.day.data == "29":
            flash("Your selected year is not a leap year so February only has 28 days")
            return redirect(url_for("make_appointment"))
        try:
            if optometrist == True and form.practice.data!=OptomThere.query.filter_by(year=form.year.data, month=form.month.data, day=form.day.data).first().practice:
                flash("We are sorry for the inconvenience but the Optomotrist is not in the practice on the day you selected")
                return redirect(url_for("make_appointment"))
            else:
                appointment = Appointments(practice=form.practice.data, appointment_type=form.appointment_type.data, user_id=user.id, need_optom=optometrist, date_time=date_time)
                db.session.add(appointment)
                db.session.commit()
                flash("Appointment has been made")
                if form.appointment_type.data == "Eye test":
                    flash("Your eye test charge will be £20")
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
    return render_template("make_appointment.html", form=form, quest_answ=quest_answ, current_year=datetime.now().year, title="Appointment form")


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
    return render_template('login.html', title='Sign In', form=form, quest_answ=quest_answ)


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
    return render_template('register.html', title='Register', form=form, quest_answ=quest_answ)


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
        return render_template('user.html', user=user, posts=posts, quest_answ=quest_answ)

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
        return render_template('edit_profile.html', quest_answ=quest_answ, title='Edit Profile', form=form)


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
        return render_template("change_password.html", quest_answ=quest_answ, title="Change password", form= form)


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
    return render_template("shop_main.html", Title="Shop", quest_answ=quest_answ, shop=shop, filter=shop_filter, filter_list=filter_list)


@app.route("/Shop_item/<shop_item_name>", methods=["GET","POST"])
def shop_item(shop_item_name):
    dic1={}
    item = Shop.query.filter_by(item_name=shop_item_name).first_or_404()
    stock = Stock.query.all()
    for i in stock:
        if i.item_id == item.id:
            dic1[i.colour] = i.quantity

    return render_template("shop_item.html", Title="Shop item", quest_answ=quest_answ, shop_item=item, stock=stock, stock_dic=dic1)


global last_stock_mail
last_stock_mail = 0
@app.route("/Shop/Cart/<username>", methods=["GET","POST"])
@login_required
def user_cart(username):
    if username != current_user.username or current_user.is_anonymous:
        return abort(404)
    global last_stock_mail
    user = User.query.filter_by(username=username).first()
    cart = Cart.query.filter_by(user_id=user.id).first()
    if request.method == "POST":
        item_id = request.form.getlist("item_id")[0]
        colour = request.form.getlist("colour")[0]
        shop = Shop.query.filter_by(id=item_id).first()
        stock = Stock.query.filter_by(item_id=shop.id, colour=colour).first()
        if stock.quantity > 0:
            new_order = Order(cart_id=cart.id, shop_id=shop.id, colour=colour)
            stock.quantity -= 1
            stock.sold += 1
            if stock.quantity <= 5 and last_stock_mail != datetime.now().date():
                msg = "Please order more of item " + str(stock.item_id) + " in " + (stock.colour)
                Config.server.sendmail("eyewisetester@gmail.com", "eyewisetester@gmail.com", msg)
                last_stock_mail = datetime.now().date()
            db.session.add(new_order)
            db.session.commit()
            flash("Item has been added")
            print("MOO")
            return redirect(url_for("shop_item", shop_item_name=shop.item_name))
            print("Bat")
        else:
            flash("This product is out of stock")
            return redirect(url_for("shop_item", shop_item_name=shop.item_name))
    print("BAT")
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
    cart.total_cost = total_cost
    db.session.commit()
    return render_template("cart.html", Title="Cart", quest_answ=quest_answ, username=username, order_item_dic=order_item_dic, Shop=Shop, user=user, cart=cart, total_cost=total_cost)


@app.route("/Super_secret_page", methods=["GET", "POST"])
def admin_page():
    if current_user.role < 1 or current_user.is_anonymous:
            return abort(404)
    else:
        return render_template("admin_page.html", Title="Admin", quest_answ=quest_answ) #TODO Add button that sends emails to people who have an appointment the following day.


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
    return render_template("user_list.html", users=users, quest_answ=quest_answ)


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
    return render_template("app_missed.html", form=form, quest_answ=quest_answ)


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
    return render_template("add_mon.html", form=form, quest_answ=quest_answ)


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

    return render_template("my_appointments.html", quest_answ=quest_answ, title="Your appointments", appointments=appointment_list)


@app.route("/Whaaaa/esf7dgf76sgf<cart_id>aftaf6ats7f<item_id>as6fa7sahafa<colour>asygasifgasfga", methods=["POST", "GET"])
@login_required
def remove_item(item_id, colour, cart_id):
    cart = Cart.query.filter_by(id=cart_id).first()
    if current_user.id != cart.user_id:
        flash("You do not have access to this page")
        return redirect(url_for("home"))
    item = Shop.query.filter_by(id=item_id).first()
    stock = Stock.query.filter_by(item_id=item_id, colour=colour).first()
    order = Order.query.filter_by(cart_id=cart.id, shop_id=item.id, colour=colour).first()
    stock.quantity += 1
    stock.sold -= 1
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for("user_cart", username=current_user.username))

@app.route("/Removing/ashjafhkajf34fhdh6fakjh7hjadfh<user_id>acsuhh76sajh<appointment_id>")
@login_required
def remove_appointment(user_id, appointment_id):
    if current_user.id != user_id and current_user.role !=3:
        flash("You do not have access to this page")
        return redirect(url_for("home"))
    user = User.query.filter_by(id=user_id).first()
    appointment = Appointments.query.filter_by(id=appointment_id).first()
    db.session.delete(appointment)
    user.total_num_app -= 1
    db.session.commit()


@app.route("/Change_role", methods=["GET", "POST"])
@login_required
def change_role():
    if current_user.role < 3 or current_user.is_anonymous:
        return abort(404)
    user_role_dic = {}
    form = ChangeRoleForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.role = form.new_role.data
        db.session.commit()
        flash(user.username + "is now role" + str(user.role))
    for user in User.query.all():
        user_role_dic[user.id] = (user.username, user.first_name, user.last_name, user.role)
    return render_template("change_role.html", quest_answ=quest_answ, title="change role", form=form, user_role_dic=user_role_dic)


@app.route("/Add_stock", methods=["GET", "POST"])
@login_required
def add_stock():
    if current_user.role < 3 or current_user.is_anonymous:
        return abort(404)
    global last_stock_mail
    form = AddStockForm()
    if form.validate_on_submit():
        try:
            stock = Stock.query.filter_by(item_id=form.id.data, colour=form.colour.data).first()
            stock.quantity += form.stock.data
            if stock.quantity < 0:
                flash("You cannot have fewer tha  0")
                return redirect(url_for("add_stock"))
        except:
            if len(Shop.query.filter_by(id=form.id.data).all()) != 0:
                stock_quantity=form.stock.data
                new_stock = Stock(colour=form.colour.data, item_id=form.id.data, quantity=stock_quantity)
                db.session.add(new_stock)
            else:
                flash("There is no item with that ID")
                return redirect(url_for("add_stock"))
        if stock.quantity <= 5 and last_stock_mail != datetime.now().date():
            msg = "Please order more of item " + str(stock.item_id) + " in " + (stock.colour)
            Config.server.sendmail("eyewisetester@gmail.com", "eyewisetester@gmail.com", msg)
            last_stock_mail = datetime.now().date()
        db.session.commit()
        return redirect(url_for("add_stock"))
    item_stock = {} #id,colour--id, name, colour, stock
    shop = Shop.query.all()
    stock = Stock.query.all()
    for item in shop:
        tem_sto= Stock.query.filter_by(item_id=item.id).all()
        for s in tem_sto:
            item_stock[str(item.id)+str(s.colour)] = [item.id, item.item_name, s.colour, s.quantity]
    return render_template("add_stock.html", quest_answ=quest_answ, title="Add stock", form=form, item_stock=item_stock)


@app.route("/Optom_dates", methods=["GET", "POST"])
@login_required
def optom_dates():
    if current_user.role < 3 or current_user.is_anonymous:
        return abort(404)
    form = OptomForm()
    if form.validate_on_submit():
        day = form.day.data
        month = form.month.data
        year = form.year.data
        practice = form.practice.data
        info = OptomThere(day=day, month=month, year=year, practice=practice)
        db.session.add(info)
        db.session.commit()
        flash("Data has been added")
    return render_template("optom_dates.html", quest_answ=quest_answ, title="Optom_dates", form=form)


@app.route("/Add_help", methods=["GET","POST"])
@login_required
def add_help():
    if current_user.role < 1 or current_user.is_anonymous:
        return abort(404)
    form = HelpForm() #TODO Add help form
    if form.validate_on_submit():
        question = form.question.data
        answer = form.answer.data
        q_a = QuestAns(question=question, answer=answer)
        db.session.add(q_a)
        db.session.commit()
        flash("Question has been added")
    return render_template("add_help.html", quest_answ=quest_answ, title="Add help", form=form)


@app.route("/Send_email", methods=["GET","POST"])
@login_required
def send_email():
    if current_user.role<3 or current_user.is_anonymous:
        return abort(404)

    for appointment in Appointments.query.all():
        if int(appointment.date_time[:4]) == datetime.now().year:
            if int(appointment.date_time[5:7]) == datetime.now().month:
                if int(appointment.date_time[8:10]) == datetime.now().day + 1:
                    user = User.query.filter_by(id=appointment.user_id).first() #TODO NE email stuff
                    msg = "We would like to remind you that you have an appointment tomorrow."
                    Config.server.sendmail("eyewisetester@gmail.com", user.email, msg)

            elif int(appointment.date_time[5:7]) == datetime.now().month+1 and int(appointment.date_time[8:10])==1:
                if (datetime.now().day==31 and datetime.now().month==(1 or 3 or 5 or 7 or 8 or 10 or 12)) or (datetime.now().day==30 and datetime.now().month==(4 or 6 or 9 or 11)) or (datetime.now().month==2 and (datetime.now().day==28 and datetime.now().year%4!=0)or datetime.now().day==29 and datetime.now().year%4==0):
                    user = User.query.filter_by(id=appointment.user_id).first()
                    msg = "We would like to remind you that you have an appointment tomorrow."
                    Config.server.sendmail("eyewisetester@gmail.com", user.email, msg)

        elif int(appointment.date_time[:4]) == datetime.now().year+1 and (int(appointment.date_time[5:7])and int(appointment.date_time[8:10]))==1:
            user = User.query.filter_by(id=appointment.user_id).first()
            msg = "We would like to remind you that you have an appointment tomorrow."
            Config.server.sendmail("eyewisetester@gmail.com", user.email, msg)

    return redirect(url_for("admin_page"))


@app.route("/add_shop_item", methods=["GET", "POST"])
@login_required
def add_shop():
    if current_user.role < 3 or current_user.is_anonymous:
        return abort(404)
    form = AddShopForm()
    if form.validate_on_submit():
        new_item = Shop(item_name=form.item_name.data, brand=form.brand.data, age=form.age.data, price=form.price.data,
                        image=form.image.data)
        db.session.add(new_item)
        db.session.commit()
        flash("Item has been added")
    return render_template("add_shop.html", quest_answ=quest_answ, title="Add shop", form=form)

@app.route("/password_recovery", methods=["GET", "POST"])
def reset_stuff_email():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        print(user)
        if user == None:
            flash("A user with your data cannot be found")
            flash("Please remember that this is case sensitive.")
            return redirect(url_for("reset_stuff_email"))
        hash = hashlib.sha1()
        hash.update(str(datetime.now()).encode('utf-8'))
        print(hash.hexdigest())
        return redirect(url_for("reset_password", user_id=user.id, salt=hash.hexdigest()))
    return render_template("pass_res_email.html", quest_answ=quest_answ, title="Email needed", form=form)


@app.route(str("/password_recovery/<user_id>/<salt>"), methods=["GET", "POST"])
def reset_password(user_id, salt):
    user = User.query.filter_by(id=user_id).first()
    form = LostPassForm()
    if form.validate_on_submit():
        user.set_password(form.new_pass)
        db.session.commit()
    return render_template("pass_reset.html", quest_answ=quest_answ, title="Pass reset", form=form)


@app.route("/statistics", methods=["GET", "POST"])
def pi_charts():
    if current_user.role < 3 or current_user.is_anonymous:
        return abort(404)
    adult_total = 0
    child_total = 0
    colour_sold = {}
    brand_sold = {}
    id_sold = {}

    for x in Shop.query.filter_by(age = "Adult").all():
        for i in Stock.query.filter_by(item_id = x.id):
            adult_total += i.sold
    for x in Shop.query.filter_by(age = "Kids").all():
        for i in Stock.query.filter_by(item_id = x.id):
            child_total += i.sold

    for item in Stock.query.all():
        if item.colour not in colour_sold:
            colour_sold[str(item.colour)] = item.sold
        else:
            colour_sold[str(item.colour)] += item.sold

    for x in Shop.query.all():
        if x.brand not in brand_sold:
            brand_sold[x.brand]= 0
        for y in Stock.query.filter_by(item_id = x.id).all():
            brand_sold[x.brand] += y.sold

    for x in Shop.query.all():
        id_sold[x.id] = 0
        for y in Stock.query.filter_by(item_id = x.id).all():
            id_sold[x.id] += y.sold

    print(child_total, adult_total, colour_sold, brand_sold)
    return render_template("statistics.html", title="Statistics", quest_answ=quest_answ, Shop=Shop, Stock=Stock, adult_total=adult_total, child_total=child_total, colour_sold=colour_sold, brand_sold=brand_sold, id_sold=id_sold)