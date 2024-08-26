from flask import request, jsonify, session
from app import app, db
from flask import abort
from app.utils.utils import set_session_expiry, is_session_valid
from app.modules.models import User, Category, Product, Comment, ProductInfo


@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'description': category.description
    } for category in categories]), 200


@app.route('/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'message': 'Category not found'}), 403

    products = Product.query.filter_by(category_id=category_id).order_by(Product.id.desc()).all()
    
    return jsonify([{
        'id': product.id,
        'name': product.product_info.name,
        'description': product.product_info.description,
    } for product in products]), 200




@app.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
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



@app.route('/categories', methods=['POST'])
def create_category():
    name = request.json.get('name')
    description = request.json.get('description', '')

    if not name:
        return jsonify({'message': 'Category name is missing.'}), 400

    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return jsonify({'message': 'Category with that name already exists.'}), 400

    new_category = Category(name=name, description=description)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'Category created successfully'}), 201


if __name__ == '__main__':
    app.run()