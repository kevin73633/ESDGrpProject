from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os

app = Flask(__name__)
CORS(app,
     origins=["http://localhost:8080"],  # Your Vue.js frontend URL
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Change to MySQL connection with your specific credentials
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("dbURL") or "mysql+mysqlconnector://" + str(environ.get("DBLOGIN")) + "@localhost:3306/Project"
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
    product = db.session.scalar(db.select(Product).filter_by(productid=productid))
    if product:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "product": product.json()
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is no product."
        }
    ), 404

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    # Basic validation
    if not all(key in data for key in ['title', 'category', 'description', 'location', 'price', 'userid']):
        return jsonify({
            "code": 400,
            "message": "Missing required fields"
        }), 400
        
    try:
        # Handle expires_at if provided
        expires_at = None
        if 'expires_at' in data and data['expires_at']:
            expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
        
        new_product = Product(
            title=data['title'],
            category=data['category'],
            description=data['description'],
            location=data['location'],
            price=data['price'],
            userid=data['userid'],
            expires_at=expires_at
        )
    
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            "code": 201,
            "data": new_product.json(),
            "message": "Product created successfully."
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"An error occurred creating the product. {str(e)}"
        }), 500

@app.route('/products/<int:productid>', methods=['PUT'])
def update_product(productid):
    try:
        product = db.session.get(Product, productid)
        if not product:
            return jsonify({
                "code": 404,
                "message": "Product not found."
            }), 404
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
    
        return jsonify({
            "code": 200,
            "data": product.json(),
            "message": "Product updated successfully."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"An error occurred updating the product. {str(e)}"
        }), 500

@app.route('/products/<int:productid>', methods=['DELETE'])
def delete_product(productid):
    try:
        product = db.session.get(Product, productid)
        if not product:
            return jsonify({
                "code": 404,
                "message": "Product not found."
            }), 404
            
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": f"Product {productid} deleted successfully."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"An error occurred deleting the product. {str(e)}"
        }), 500

# Route to get products by user
@app.route('/users/<string:userid>/products', methods=['GET'])
def get_user_products(userid):
    productlist = db.session.scalars(db.select(Product).filter_by(userid=userid)).all()
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
            "message": f"No products found for user {userid}."
        }
    ), 404

# Route to get products by category
@app.route('/products/category/<string:category>', methods=['GET'])
def get_products_by_category(category):
    productlist = db.session.scalars(db.select(Product).filter_by(category=category)).all()
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
            "message": f"No products found in category {category}."
        }
    ), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)