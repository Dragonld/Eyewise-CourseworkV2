from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True, unique=False)
    last_name = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    telephone_num = db.Column(db.String(14), index=True)
    address1 = db.Column(db.String(64))
    address2 = db.Column(db.String(64))
    town_city = db.Column(db.String(64))
    postcode = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    total_num_app = db.Column(db.Integer)
    app_missed = db.Column(db.Integer)
    total_mon_spen = db.Column(db.Float)
    perc_app_attend = db.Column(db.Float)
    mon_per_appoint = db.Column(db.Float)

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic') #convert to cart
    admin = db.Column(db.Boolean, index=True)
    role = db.Column(db.Integer)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post: {}>'.format(self.body)


class Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    need_optom = db.Column(db.Boolean)
    practice = db.Column(db.String)
    date_time = db.Column(db.DateTime, index=True, unique=True)
    time = db.Column(db.Time, index=True)
    date = db.Column(db.Date, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return '<Appointment: {}>'.format(self.date_time)


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String, index=True)
    brand = db.Column(db.String, index=True)
    sex = db.Column(db.String(10), index=True)
    price = db.Column(db.Float)
    image = db.Column(db.String)

    def __repr__(self):
        return '<Shop: {}>'.format(self.item_name)


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    colour = db.Column(db.String, index=True)
    quantity = db.Column(db.Integer)
    item_id = db.Column(db.Integer, db.ForeignKey("shop.id"))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    shop_id = db.Column(db.Integer, db.ForeignKey("shop.id"))

    def __repr__(self):
        return '<order: {}>'.format(self.id)


@login.user_loader
def load_user(i):
    return User.query.get(int(i))

