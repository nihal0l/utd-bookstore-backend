from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# --- DATABASE CONFIGURATION ---
DB_USER = os.environ.get('DB_USER', 'store_admin')
DB_PASS = os.environ.get('DB_PASS', 'BookstoreAdmin123')
DB_NAME = os.environ.get('DB_NAME', 'utd_store')
DB_HOST = os.environ.get('DB_HOST', '34.57.202.58')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
# --- ROUTES ---

# 1. GET ALL PRODUCTS
@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        return jsonify([{
            "id": p.id, 
            "name": p.name, 
            "price": p.price,
            "category": p.category,
            "description": p.description
        } for p in products]), 200
    except Exception as e:
        return jsonify({"error": "Database connection failed", "details": str(e)}), 500

# 2. GET SINGLE PRODUCT
@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            return jsonify({
                "id": product.id, 
                "name": product.name, 
                "price": product.price,
                "category": product.category,
                "description": product.description
            }), 200
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": "Query failed", "details": str(e)}), 500

# 3. POST NEW ORDER (Checkout)
@app.route('/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        
        # Validation: Ensure required fields are present
        if not data.get('student_name') or not data.get('product_id'):
            return jsonify({"error": "Missing student_name or product_id"}), 400

        new_order = Order(
            student_name=data.get('student_name'),
            product_id=data.get('product_id'),
            quantity=data.get('quantity', 1)
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            "status": "Success", 
            "message": "Order placed!", 
            "order_id": new_order.id
        }), 201
    except Exception as e:
        db.session.rollback() # Reverts changes if something goes wrong
        return jsonify({"error": "Failed to place order", "details": str(e)}), 500

# --- RUN THE APP ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)