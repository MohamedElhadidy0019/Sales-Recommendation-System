import pandas as pd
from itertools import chain

from flask import Flask, request, jsonify
app = Flask(__name__)


def get_frequently_bought_together(data_path:str, product_name:str):
    test_code = product_name
    df = pd.read_csv(data_path, usecols=['InvoiceNo', 'StockCode', 'Quantity'])
    df = df[df['Quantity'] > 0]
    # drop duplicates
    df = df.drop_duplicates()
    # drop na
    df = df.dropna()
    # get unique StockCode
    stock_codes = df['StockCode'].unique()

    df = df.groupby('InvoiceNo')['StockCode'].apply(list).reset_index(name='StockCode')
    # get me each row that has the test code in one of the element os Stockcode
    test_df = df[df['StockCode'].apply(lambda lst: test_code in lst)]
    # Assuming df['StockCode'] is a column containing lists of strings
    all_stock_codes = list(chain.from_iterable(test_df['StockCode']))

    # Count the frequency of each word
    word_freq = {}
    for word in all_stock_codes:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1

    # Sort the list by frequency
    sorted_word_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    # remove from the list the test_code if exist
    sorted_word_freq = [item for item in sorted_word_freq if item[0] != test_code]
    if(len(sorted_word_freq) > 10):
        sorted_word_freq = sorted_word_freq[:10]
    return sorted_word_freq

@app.route('/get_frequently_bought_together', methods=['POST'])
def frequently_bought_together():
    data = request.get_json()
    product_name = data.get('product_name')

    if product_name is None:
        return jsonify({'error': 'Data path or product name is missing'}), 400

    product_name = str(product_name)

    result = get_frequently_bought_together('Dataset.csv', product_name)
    formatted_result = [{'StockCode': item[0], 'Frequency': item[1]} for item in result]
    
    return jsonify({'frequently_bought_together': formatted_result})

if __name__ == '__main__':
    app.run(debug=True)


