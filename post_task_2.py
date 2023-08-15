import requests

data = {'item_name': '22778'}  # Replace with the item name you want to find similar items for

response = requests.post('http://127.0.0.1:5000/get_similar_items', json=data)

if response.status_code == 200:
    similar_items = response.json()['similar_items']
    for item in similar_items:
        print(f"StockCode: {item['StockCode']}, Description: {item['Description']}, Similarity: {item['Similarity']}")
else:
    print('Error:', response.json())
