import requests

data = {
    'product_name': '22748'  # Replace with the desired product code
}

response = requests.post('http://127.0.0.1:5000/get_frequently_bought_together', json=data)

if response.status_code == 200:
    result = response.json()['frequently_bought_together']
    for item in result:
        print(f"StockCode: {item['StockCode']}, Frequency: {item['Frequency']}")
else:
    print('Error:', response.json())
