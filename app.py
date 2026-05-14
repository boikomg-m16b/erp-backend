from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Кажемо диспетчеру, де буде лежати наш склад (база даних)
# Це створить файл erp_base.db прямо в твоїй папці
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///erp_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Запускаємо нашого "комірника"
db = SQLAlchemy(app)

# ==========================================
# МОДЕЛІ (КРЕСЛЕННЯ НАШИХ ТАБЛИЦЬ)
# ==========================================

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.Float, default=0.0)
    # Зовнішній ключ: замовлення обов'язково належить конкретному клієнту
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

# Той самий "міст" для зв'язку Багато-до-Багатьох
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Посилання на конкретне замовлення
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    # Посилання на конкретний товар
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

# ==========================================

# Ця команда фізично створює таблиці в базі, якщо їх ще немає
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "База даних підключена! Таблиці створено успішно."

# ==========================================
# API МАРШРУТИ (БІЗНЕС-ЛОГІКА)
# ==========================================

# 1. Створення клієнта
@app.route('/client', methods=['POST'])
def create_client():
    # Отримуємо дані (JSON), які нам прислали
    data = request.get_json()
    
    # Перевіряємо, чи передали ім'я
    if not data or 'name' not in data:
        return jsonify({"error": "Ім'я клієнта обов'язкове!"}), 400
    
    # Створюємо об'єкт (копіюємо з креслення)
    new_client = Client(name=data['name'])
    
    # Віддаємо команду комірнику: поклади в базу і збережи
    db.session.add(new_client)
    db.session.commit()
    
    return jsonify({"message": f"Клієнта {new_client.name} успішно створено!", "id": new_client.id}), 201

# 2. Створення товару
@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Назва та ціна обов'язкові!"}), 400
        
    new_product = Product(name=data['name'], price=data['price'])
    
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify({"message": f"Товар {new_product.name} додано на склад!", "id": new_product.id}), 201
# 3. Створення замовлення (Найскладніший етап)
@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    
    # Правило 1: Перевіряємо, чи є взагалі дані
    if not data or 'client_id' not in data or 'product_ids' not in data:
        return jsonify({"error": "client_id та product_ids (список) обов'язкові!"}), 400
        
    client_id = data['client_id']
    product_ids = data['product_ids'] # Очікуємо список ID товарів, наприклад [1, 2]
    
    # Правило 2: У замовленні має бути хоча б один товар
    if not product_ids:
        return jsonify({"error": "Замовлення не може бути порожнім!"}), 400
        
    # Правило 3: Перевіряємо, чи існує такий клієнт
    client = db.session.get(Client, client_id)
    if not client:
        return jsonify({"error": "Клієнта з таким ID не знайдено!"}), 404
        
    # Правило 4: Рахуємо суму (бізнес-логіка ERP)
    total = 0
    for p_id in product_ids:
        product = db.session.get(Product, p_id)
        if product:
            total += product.price
        else:
            return jsonify({"error": f"Товар з ID {p_id} не знайдено на складі!"}), 404
            
    # Правило 5: Створюємо чек (Замовлення)
    new_order = Order(client_id=client.id, total_amount=total)
    db.session.add(new_order)
    db.session.commit() # Зберігаємо зараз, щоб база видала нам ID замовлення (new_order.id)
    
    # Правило 6: "Кладемо товари в коробку" (Проміжна таблиця)
    for p_id in product_ids:
        order_item = OrderItem(order_id=new_order.id, product_id=p_id, quantity=1)
        db.session.add(order_item)
        
    db.session.commit() # Фінальне збереження
    
    return jsonify({
        "message": "Замовлення успішно створено!",
        "order_id": new_order.id,
        "total_amount": total
    }), 201

if __name__ == '__main__':
    app.run(debug=True)