from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from sklearn.metrics.pairwise import cosine_similarity
from typing import List


app = Flask(__name__)

def calculate_cosine_similarity(vec_a, vec_b):
    vec_a = np.array(vec_a).reshape(1, -1)
    vec_b = np.array(vec_b).reshape(1, -1)
    
    similarity = cosine_similarity(vec_a, vec_b)
    return similarity[0][0]

def read_data(data_path:str='Dataset.csv')-> pd.DataFrame:
    df = pd.read_csv(data_path, usecols=['StockCode', 'Description'])
    df = df.dropna()
    df = df.drop_duplicates()
    return df

   
df = read_data('Dataset.csv')
item_tuples = [(row['StockCode'], row['Description']) for index, row in df.iterrows()]
module_url = "https://tfhub.dev/google/universal-sentence-encoder/4" #@param ["https://tfhub.dev/google/universal-sentence-encoder/4", "https://tfhub.dev/google/universal-sentence-encoder-large/5"]
model = hub.load(module_url)
def embed(input):
  return model(input)


def get_similar_items(item_name:str,df:pd.DataFrame, item_tuples, model)-> List[str]:
    test_item = item_name
    # want the longest description for the item from the df
    all_description = df[df['StockCode'] == test_item]['Description']
    # det the longest str in all_description
    longest_description = max(all_description, key=len)
    print(longest_description)

    description_embedding = embed([longest_description])

    # get the 10 most similar items from item_tuples using cosine similarity
    similar_items = []
    for item in item_tuples:
        if(item[0] == test_item):
            continue
        item_embedding = embed([item[1]])
        similarity = cosine_similarity(description_embedding, item_embedding)
        # if similairty is higher than all similarities in similar_items, add it to similar_items 
        if len(similar_items) < 10 and similarity > 0.4:
            similar_items.append((item[0], item[1], similarity))
        else:
            for i in range(len(similar_items)):
                if similarity > similar_items[i][2]:
                    similar_items[i] = (item[0], item[1], similarity)
                    break

    return similar_items    

@app.route('/get_similar_items', methods=['POST'])
def get_similar_items_endpoint():
    data = request.get_json()
    item_name = data.get('item_name')
    
    if item_name is None:
        return jsonify({'error': 'Item name is missing'}), 400
    item_name = str(item_name)
    similar_items = get_similar_items(item_name, df, item_tuples, model)
    
    result = [{'StockCode': item[0], 'Description': item[1], 'Similarity': item[2][0][0]} for item in similar_items]
    return jsonify({'similar_items': result})


if __name__ == '__main__':
    app.run(debug=True)

