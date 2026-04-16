from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # This allows your UTD Frontend to talk to this API

# --- DATABASE PLACEHOLDER ---
# Member 3 (DBA) will give you the real connection string later.
# For now, we use a simple list to simulate the database.
inventory = [
    {
        "id": 1, 
        "name": "Champion UTD Fleece Hoodie", 
        "price": 49.99, 
        "category": "Apparel",
        "description": "UTD Orange fleece with white embroidery."
    },
    {
        "id": 2, 
        "name": "UTD Stainless Tumbler", 
        "price": 24.50, 
        "category": "Accessories",
        "description": "Matte green, 20oz vacuum insulated."
    }
]

# --- ROUTES ---

# 1. GET ALL PRODUCTS (The Catalog)
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(inventory), 200

# 2. GET SINGLE PRODUCT (Product Details)
@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((item for item in inventory if item["id"] == product_id), None)
    if product:
        return jsonify(product), 200
    return jsonify({"error": "Product not found"}), 404

# 3. POST ORDER (Simulated Checkout)
@app.route('/order', methods=['POST'])
def create_order():
    order_data = request.json
    # In the final version, Member 3 will help you save this to SQL.
    print(f"New Order Received from {order_data.get('student_name')}")
    return jsonify({"status": "Success", "message": "Order placed for UTD Bookstore!"}), 201

# --- RUN THE APP ---
if __name__ == "__main__":
    # Cloud Run requires the app to listen on the port defined by the PORT env var.
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)