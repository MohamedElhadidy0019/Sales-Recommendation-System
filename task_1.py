from flask import Flask, request, jsonify
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
from typing import List
from surprise import dump

app = Flask(__name__)

def preprocess(dataset_name: str = 'Dataset.csv') -> pd.DataFrame: 
    # Load the dataset (excluding Description and InvoiceDate columns)
    df = pd.read_csv(dataset_name, usecols=['CustomerID', 'StockCode', 'Quantity'])

    # Preprocess the data (drop NaN rows and convert to integer)
    df.dropna(subset=['CustomerID', 'StockCode', 'Quantity'], inplace=True)
    # drop StockCode with non-numeric values
    df = df[df['StockCode'].str.isnumeric()]

    df = df.astype({'CustomerID': int, 'StockCode': int, 'Quantity': int})
    return df


def split_df(df: pd.DataFrame, test_size: float = 0.2) -> (pd.DataFrame, pd.DataFrame):
    users = df['CustomerID'].unique()
    test_len = test_size*(len(users))
    test_customers = users[:int(test_len)]
    train_customers = users[int(test_len):]

    # make the train df have unique customers from test df to avoid data leakage
    df_train = df[df['CustomerID'].isin(train_customers)]
    
    df_test = df[df['CustomerID'].isin(test_customers)]
    
    # Create  Surprise Dataset
    reader = Reader(rating_scale=(1, 5))
    trainset = Dataset.load_from_df(df_train[['CustomerID', 'StockCode', 'Quantity']], reader)
    testset = Dataset.load_from_df(df_test[['CustomerID', 'StockCode', 'Quantity']], reader)

    # the folowing 2 lines were just work arounds in order to make itterable objects suitable for the SVD fit method
    trainset, _ = train_test_split(trainset, test_size=0.01, random_state=42)
    _, testset = train_test_split(testset, test_size=0.09, random_state=42)

    return trainset, testset

# Function to get item recommendations for a given user
def get_item_recommendations(user_id:int, dataset_path:str, model, num_recommendations=5)->List[int]:
    # Load the dataset
    df =preprocess(dataset_path)
    items_already_purchased = df[df['CustomerID'] == user_id]['StockCode'].tolist()
    
    # Get all item IDs
    item_ids = df['StockCode'].unique()
    
    # Remove items already purchased
    items_to_predict = [item_id for item_id in item_ids if item_id not in items_already_purchased]
    
    # Predict ratings for items
    predictions = [model.predict(user_id, item_id) for item_id in items_to_predict]
    
    # Sort predictions by predicted rating
    predictions.sort(key=lambda x: x.est, reverse=True)
    
    # Get top N recommended items
    top_recommendations = [int(prediction.iid) for prediction in predictions[:num_recommendations]]
    return top_recommendations

loaded_model = dump.load('trained_model.pkl')[1]
dataset_path = 'Dataset.csv'

@app.route('/get_recommendations', methods=['POST'])
def get_item_recommendations_flask():
    data = request.get_json()
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify({'error': 'User ID is missing'}), 400
    print('GOT ID: ', user_id)
    user_id = int(user_id)
    

    recommendations = get_item_recommendations(user_id, dataset_path, loaded_model)
    print('returning recommendations: ', recommendations)
    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True)


