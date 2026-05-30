from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///factory_erp.db'


db = SQLAlchemy(app)

class Client(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   name = db.Column(db.String(100),nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100),nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)


@app.route('/')
def hello_factory():
    return "All good!"

@app.route('/client', methods=['POST'])
def create_client():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    new_client = Client(name=data['name'])
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"message": "Client created successfully", "id": new_client.id}), 201

@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Something is missed"}), 400
    new_product = Product(name=data['name'], price = data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully", "id": new_product.id}), 201

@app.route('/products', methods = ['GET'])
def get_all_products():
    products = Product.query.all()
    result = []
    for product in products:
        result.append({"id": product.id, "name": product.name, "price": product.price})
    return jsonify(result), 200

@app.route('/product/<int:id>', methods = ['GET'])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 400

    return jsonify({"id": product.id, "name": product.name, "price": product.price}), 200

@app.route('/product/<int:id>', methods = ['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 201

@app.route('/product/<int:id>', methods = ['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product is not found"}), 400
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Something is missed"}), 400
    product.name = data['name']
    product.price = data['price']
    db.session.commit()
    return jsonify({"message": "Product updated successfully", "id": product.id}), 200

@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    if not 'quantity' in data or not 'client_id' in data or not 'product_id' in data:
        return jsonify({"error": "Missing data"}), 400
    client = Client.query.get(data['client_id'])
    product = Product.query.get(data['product_id']) 
    if not client or not product:
        return jsonify({"error": "Client or Product not found"}), 404
    calculated_total = product.price * data['quantity']
    new_order = Order(client_id = data['client_id'], product_id = data['product_id'], quantity = data['quantity'], total_price=calculated_total)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "order created successfully", "id": new_order.id}), 201

@app.route('/orders', methods = ['GET'])
def get_all_orders():
    orders = Order.query.all()
    result = []
    for order in orders:
        client = Client.query.get(order.client_id)
        product = Product.query.get(order.product_id)
        result.append({
        "order_id": order.id,
        "client_name": client.name,   
        "product_name": product.name,  
        "quantity": order.quantity
        })
    return jsonify(result), 200

@app.route('/orders/client/<int:client_id>', methods=['GET'])
def get_client_orders(client_id):
    orders = Order.query.filter_by(client_id=client_id).all()
    result = []
    for order in orders:
        client = Client.query.get(order.client_id)
        product = Product.query.get(order.product_id)
        result.append({
        "order_id": order.id,
        "client_name": client.name,   
        "product_name": product.name,  
        "quantity": order.quantity,
        "total_price": order.total_price
        })
    return jsonify(result), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

