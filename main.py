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

# --- DATABASE MODELS (Matched to your Screenshots) ---

class Product(db.Model):
    __tablename__ = 'Products'
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(150), nullable=True)
    Price = db.Column(db.Float, nullable=True)
    Category = db.Column(db.String(100), nullable=True)
    ImageURL = db.Column(db.String(500), nullable=True)

class Order(db.Model):
    __tablename__ = 'Orders'
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProductID = db.Column(db.Integer, nullable=True)
    StudentName = db.Column(db.String(150), nullable=True)

# --- ROUTES ---

# 1. GET ALL PRODUCTS
@app.route('/products', methods=['GET'])
def get_products():
    try:
        category_query = request.args.get('category')
        if category_query:
            products = Product.query.filter(Product.Category.ilike(category_query)).all()
        else:
            products = Product.query.all()

        return jsonify([{
            "id": p.ID, 
            "name": p.Name, 
            "price": float(p.Price) if p.Price else 0,
            "category": p.Category,
            "image_url": p.ImageURL
        } for p in products]), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

# 2. POST NEW ORDER (Checkout)
@app.route('/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        
        # Mapping frontend keys to DB Column names
        new_order = Order(
            StudentName=data.get('student_name'),
            ProductID=data.get('product_id')
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({"status": "Success", "order_id": new_order.OrderID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Order failed", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)