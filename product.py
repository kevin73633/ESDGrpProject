from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os

app = Flask(__name__)
# Change to MySQL connection with your specific credentials
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/Project"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Product Model - Updated to match your SQL structure
class Product(db.Model):
    __tablename__ = 'product'  # Match the exact table name from your SQL
    
    productid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    userid = db.Column(db.String(64), nullable=False)
    
    def json(self):
        dto = {
            'productid': self.productid,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'location': self.location,
            'price': self.price,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'userid': self.userid
        }

        # dto['order_item'] = []
        # for oi in self.order_item:
        #     dto['order_item'].append(oi.json())

        return dto

# Routes for Product CRUD operations
@app.route('/products', methods=['GET'])
def get_products():
    productlist = db.session.scalars(db.select(Product)).all()
    if len(productlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "products": [product.json() for product in productlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no products."
        }
    ), 404

@app.route('/products/<int:productid>', methods=['GET'])
def get_product(productid):
    product = Product.query.get_or_404(productid)
    return jsonify(product.to_dict())

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    # Basic validation
    if not all(key in data for key in ['title', 'category', 'description', 'location', 'price', 'userid']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_product = Product(
        title=data['title'],
        category=data['category'],
        description=data['description'],
        location=data['location'],
        price=data['price'],
        userid=data['userid'],
        expires_at=data.get('expires_at')
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify(new_product.to_dict()), 201

@app.route('/products/<int:productid>', methods=['PUT'])
def update_product(productid):
    product = Product.query.get_or_404(productid)
    data = request.get_json()
    
    # Update fields if they exist in the request
    if 'title' in data:
        product.title = data['title']
    if 'category' in data:
        product.category = data['category']
    if 'description' in data:
        product.description = data['description']
    if 'location' in data:
        product.location = data['location']
    if 'price' in data:
        product.price = data['price']
    if 'expires_at' in data:
        product.expires_at = data['expires_at']
    
    db.session.commit()
    
    return jsonify(product.to_dict())

@app.route('/products/<int:productid>', methods=['DELETE'])
def delete_product(productid):
    product = Product.query.get_or_404(productid)
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': f'Product {productid} deleted successfully'})

# Route to get products by user
@app.route('/users/<string:userid>/products', methods=['GET'])
def get_user_products(userid):
    product = db.session.scalar(db.select(Product).filter_by(userid=userid))
    if product:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "user": [product.json()]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is no product."
        }
    ), 404

# Route to get products by category
@app.route('/products/category/<string:category>', methods=['GET'])
def get_products_by_category(category):
    products = Product.query.filter_by(category=category).all()
    return jsonify([product.to_dict() for product in products])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)