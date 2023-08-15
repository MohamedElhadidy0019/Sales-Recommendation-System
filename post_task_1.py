import requests

data = {'user_id': 17850}
response = requests.post('http://127.0.0.1:5000/get_recommendations', json=data)

if response.status_code == 200:
    try:
        recommendations = response.json()['recommendations']
        print('Top recommendations:', recommendations)
    except requests.exceptions.JSONDecodeError:
        print('Response content:', response.content)
        print('Error:', response.text)
else:
    print('Error:', response.json())