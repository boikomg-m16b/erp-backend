import requests

# 1. Тестуємо створення клієнта
print("Створюємо клієнта...")
client_response = requests.post(
    'http://127.0.0.1:5000/client', 
    json={"name": "ТОВ Київський Завод"}
)
print(client_response.json())

# 2. Тестуємо створення товару
print("\nСтворюємо товар...")
product_response = requests.post(
    'http://127.0.0.1:5000/product', 
    json={"name": "Пляшка 1Л", "price": 15.50}
)
print(product_response.json())

# 3. Тестуємо створення замовлення
print("\nСтворюємо замовлення...")
# Ми кажемо: Клієнт №1 (ТОВ Київський Завод) купує Товар №1 (Пляшка 1Л) два рази
order_response = requests.post(
    'http://127.0.0.1:5000/order', 
    json={
        "client_id": 1, 
        "product_ids": [1, 1] 
    }
)
print(order_response.json())