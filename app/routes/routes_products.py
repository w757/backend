from flask import request, jsonify, session
from app import app, db
from app.modules.models import User, Category, Product, Comment, ProductInfo
from flask import abort
from app.utils.utils import set_session_expiry, is_session_valid
from werkzeug.utils import secure_filename
import os
import base64



@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': product.id,
        'name': product.product_info.name,
        'description': product.product_info.description,
    } for product in products]), 200

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    comments = Comment.query.filter_by(product_info_id=product.product_info.id).all()
    comments_data = [{
        'id': comment.id,
        'text': comment.text,
        'user_id': comment.user_id
    } for comment in comments]

    if not comments_data:
        comments_data = "Nie ma jeszcze komentarzy dla tego produktu."

    return jsonify({
        'id': product.id,
        'name': product.product_info.name,
        'description': product.product_info.description,
        'comments': comments_data
    }), 200

@app.route('/products', methods=['POST'])
def create_product():
    name = request.json.get('name')
    category_id = request.json.get('category_id')
    product_info_name = request.json.get('product_info_name')
    product_info_description = request.json.get('product_info_description', '')
    comments = request.json.get('comments', [])

    if not name or not category_id or not product_info_name:
        return jsonify({'message': 'Product name, category_id, or product_info_name is missing.'}), 400

    existing_category = Category.query.get(category_id)
    if not existing_category:
        return jsonify({'message': 'Category with that category_id does not exist.'}), 404

    new_product_info = ProductInfo(name=product_info_name, description=product_info_description, category_id=category_id)
    db.session.add(new_product_info)
    db.session.commit()

    # # Adding comments if provided
    # if comments:
    #     for comment_text in comments:
    #         if comment_text:
    #             new_comment = Comment(text=comment_text, user_id=session.get('user_id'), product_info_id=new_product_info.id)
    #             db.session.add(new_comment)
    #     db.session.commit()

    new_product = Product(name=name, category_id=category_id, product_info_id=new_product_info.id)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product created successfully'}), 201

# get image 

UPLOAD_FOLDER = 'public/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/images/<image_name>', methods=['GET'])
def get_image(image_name):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    
    if os.path.isfile(image_path):
        with open(image_path, 'rb') as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
            return jsonify({'image_data': image_data}), 200
    else:
        return jsonify({'message': 'Image not found'}), 404
