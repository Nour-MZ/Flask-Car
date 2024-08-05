from flask import Flask, jsonify, request, render_template
import csv
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
import random
from itertools import islice

app = Flask(__name__)


cars = []
with open('Car_Data.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        cars.append(row)

def create_combined_string(car):
    return f"{car['brand']} {car['model']} {car['year']} {car['color']} "

combined_strings = [create_combined_string(car) for car in cars]

tfidf_vectorizer = TfidfVectorizer(max_df=0.2)
tfidf_matrix = tfidf_vectorizer.fit_transform(combined_strings)

car_data = pd.read_csv('Car_Data.csv')
car_data['combined'] = car_data['brand'] + ' ' + car_data['model'] + ' ' + car_data['year'].astype(str) + ' ' + car_data['color']  

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')



@app.route('/search', methods=['GET'])
def search_cars():
    query = request.args.get('query', '')

    if query == "":
        return 
    
    querio = query.lower().split()
    matches = []
     
    for car in cars:      
        if all(query.lower() in create_combined_string(car).lower() for query in querio): 
            matches.append(car)
        if(len(matches)>25):
            break
    return jsonify(matches)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query')
    query = query.lower()
    
    
    if len(query) < 2:
        return jsonify([])
    
    filtered_words = [word for word in combined_strings if query in word.lower()][:10]
    print(filtered_words)
    return jsonify(filtered_words)


@app.route('/recommend', methods=['GET'])
def recommend_cars():
    query = request.args.get('items')
      
    query = query.lower().split(",")

    results = []
    if query:
        similarities = []
        for word in query:
            query_vector = tfidf_vectorizer.transform([word]).toarray()[0]
            similarity = cosine_similarity(tfidf_matrix.toarray(), [query_vector])
            similarities.append(similarity.flatten())

        combined_similarities = np.sum(similarities, axis=0)
        top_results = np.argsort(combined_similarities)[::-1]

        # Group results by query term
        query_terms = {}
        for idx in top_results:
            car_info = car_data.iloc[idx].to_dict()
            query_term = [word for word in query if word in car_info['combined'].lower()]
            if query_term:
                query_term = query_term[0]
                if query_term not in query_terms:
                    query_terms[query_term] = []
                query_terms[query_term].append(car_info)

        
        results = []
        limited_results = []
        p=3
        for query_term, cars in query_terms.items():
            random.shuffle(cars)
            limited_results.extend(cars[:p]) 
            if p > 2:
                p = p-1
             # Limit to 2 cars per query term
            if len(limited_results) >= 10:
                break

        results = [{'car': car, 'score': float(combined_similarities[idx])} for idx, car in enumerate(limited_results)]

        return jsonify(results)

        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)