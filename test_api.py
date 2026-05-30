import requests

print("Створюємо клієнта...")
client_response = requests.post(
    'http://127.0.0.1:5000/client', 
    json={"name": "ТОВ Київський Завод"}
)
print(client_response.json())

print("\nСтворюємо товар...")
product_response = requests.post(
    'http://127.0.0.1:5000/product', 
    json={"name": "Пляшка 1Л", "price": 15.50}
)
print(product_response.json())

print("\nСтворюємо замовлення...")
order_response = requests.post(
    'http://127.0.0.1:5000/order', 
    json={
        "client_id": 1, 
        "product_ids": [1, 1] 
    }
)
print(order_response.json())
