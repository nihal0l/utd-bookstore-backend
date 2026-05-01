from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# --- DATABASE CONFIGURATION ---
# Pulling from Cloud Run environment variables for security
DB_USER = os.environ.get('DB_USER', 'store_admin')
DB_PASS = os.environ.get('DB_PASS', 'BookstoreAdmin123')
DB_NAME = os.environ.get('DB_NAME', 'utd_store')
DB_HOST = os.environ.get('DB_HOST', '34.57.202.58')

# Connection string using PyMySQL driver
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---
# Matched exactly to your "DESCRIBE" screenshots

class Product(db.Model):
    __tablename__ = 'Products'
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(150))
    Price = db.Column(db.Numeric(10, 2))
    Category = db.Column(db.String(100))
    ImageURL = db.Column(db.String(500))

class Order(db.Model):
    __tablename__ = 'Orders'
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProductID = db.Column(db.Integer)
    StudentName = db.Column(db.String(150))
    # Timestamp is DEFAULT_GENERATED in your DB, so we don't need to define it here

# --- ROUTES ---

# 1. GET ALL PRODUCTS (With Case-Insensitive Category Filter)
@app.route('/products', methods=['GET'])
def get_products():
    try:
        category_query = request.args.get('category')
        
        if category_query:
            # Using .ilike() for robust filtering (e.g., graduation vs Graduation)
            products = Product.query.filter(Product.Category.ilike(category_query)).all()
        else:
            products = Product.query.all()

        return jsonify([{
            "id": p.ID, 
            "name": p.Name, 
            "price": float(p.Price) if p.Price else 0.0,
            "category": p.Category,
            "image_url": p.ImageURL
        } for p in products]), 200
    except Exception as e:
        return jsonify({"error": "Database retrieval failed", "details": str(e)}), 500

# 2. GET SINGLE PRODUCT (Details View)
@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            return jsonify({
                "id": product.ID, 
                "name": product.Name, 
                "price": float(product.Price) if product.Price else 0.0,
                "category": product.Category,
                "image_url": product.ImageURL
            }), 200
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": "Query failed", "details": str(e)}), 500

# 3. POST NEW ORDER (Checkout)
@app.route('/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        
        # We map lowercase frontend keys to PascalCase DB columns
        new_order = Order(
            StudentName=data.get('student_name'),
            ProductID=data.get('product_id')
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            "status": "Success", 
            "message": "Order placed!", 
            "order_id": new_order.OrderID
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Checkout failed", "details": str(e)}), 500

# --- RUN APP ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)