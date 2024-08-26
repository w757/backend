from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(1000))

    def __repr__(self):
        return '<Category %r>' % self.name

class ProductInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products_info', lazy=True))
    comments = db.relationship('Comment', backref='product_info', lazy=True)

    def __repr__(self):
        return '<ProductInfo %r>' % self.name

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(256)) #new
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    product_info_id = db.Column(db.Integer, db.ForeignKey('product_info.id'), nullable=False)
    product_info = db.relationship('ProductInfo', backref=db.backref('products', lazy=True))



    def __repr__(self):
        return '<Product %r>' % self.name

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    product_info_id = db.Column(db.Integer, db.ForeignKey('product_info.id'), nullable=False)
