from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# --- DATABASE CONFIGURATION ---
# These values will be pulled from Cloud Run Environment Variables for security
DB_USER = os.environ.get('DB_USER', 'store_admin')
DB_PASS = os.environ.get('DB_PASS', 'BookstoreAdmin123')
DB_NAME = os.environ.get('DB_NAME', 'utd_store')
DB_HOST = os.environ.get('DB_HOST', '34.57.202.58')

# Connection string for MySQL using the PyMySQL driver
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODEL ---
# This tells Flask what the 'products' table looks like in SQL
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)

# --- ROUTES ---

# 1. GET ALL PRODUCTS (From the Real Database)
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
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id, 
            "name": product.name, 
            "price": product.price,
            "description": product.description
        }), 200
    return jsonify({"error": "Product not found"}), 404

# --- RUN THE APP ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)