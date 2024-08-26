from flask import request, jsonify, session
from app import app, db
from app.modules.models import User, Category, Product, Comment, ProductInfo
from flask import abort
from app.utils.utils import set_session_expiry, is_session_valid
#from flask_session import Session
from flask.sessions import SecureCookieSessionInterface
from flask_cors import CORS
from app.modules.models import User
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, verify_jwt_in_request

from flask import request, jsonify
from app import app, db
from app.modules.models import User
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

import json
from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager


app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  
app.config['SESSION_COOKIE_SECURE'] = False 
app.config['SESSION_COOKIE_HTTPONLY'] = False


CORS(app, supports_credentials=True, resources={r"127.0.0.1:5000/*": {"origins": "*"}})


app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config['TIMEZONE'] = 'Europe/Warsaw'
#app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=5)

jwt = JWTManager(app)

@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*') 
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization, Set-Cookie')
    response.headers.add('Access-Control-Allow-Credentials', 'true')  
    return response



@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

@app.route('/verify_token', methods=["POST"])
@jwt_required(optional=True)
def verify_token():
    try:
        verify_jwt_in_request()
        return jsonify({"valid": True}), 200
    except Exception as e:
        return jsonify({"valid": False, "message": str(e)}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        # Uzyskaj identyfikator zalogowanego użytkownika z tokena JWT
        current_user = get_jwt_identity()
        # Tutaj możesz użyć identyfikatora, aby pobrać więcej informacji o użytkowniku z bazy danych
        # Na przykład:
        # user = User.query.filter_by(id=current_user).first()
        return jsonify(logged_in_as=current_user), 200
    except Exception as e:
        return jsonify(message=str(e)), 500


@app.route('/token', methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email != "test" or password != "test":
        return {"msg": "Wrong email or password"}, 401

    access_token = create_access_token(identity=email)
    response = {"access_token":access_token}
    return response

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route('/profile')
@jwt_required()
def my_profile():
    response_body = {
        "name": "Nagato",
        "about" :"Hello! I'm a full stack developer that loves python and javascript"
    }

    return response_body





# Register endpoint
@app.route('/register', methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    # Create new user
    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        first_name=first_name,
        last_name=last_name
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Login endpoint
@app.route('/login', methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

# Protected profile endpoint
@app.route('/profile')
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }), 200


@app.route('/add_comment', methods=["POST"])
@jwt_required()
def add_comment():
    try:
        data = request.json
        user_id = get_jwt_identity()
        product_info_id = data.get("product_info_id")
        text = data.get("text")

        # Sprawdź, czy produkt istnieje
        product = Product.query.get(product_info_id)
        if not product:
            return jsonify({"message": "Product not found"}), 404

        # Stwórz nowy komentarz
        new_comment = Comment(
            user_id=user_id,
            product_info_id=product_info_id,
            text=text
        )
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({"message": "Comment added successfully"}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500


