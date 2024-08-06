import google.generativeai as genai
from flask import Flask, jsonify, request, render_template
import csv
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
import random

import difflib

genai.configure(api_key="AIzaSyBLFXyxwRNYR8EcJZi7jbpXRJfdDw68Tc0")



model = genai.GenerativeModel('gemini-1.5-flash')



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

colors = ['red','white','green','black','gray', 'blue']

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
    
    return jsonify(filtered_words)


@app.route('/recommend', methods=['GET'])
def recommend_cars():
    query = request.args.get('items')
      
    query = query.lower().split(",")

    print("query", query)

    results = []
    if query:
        response = model.generate_content(f"in 1 list seperate using commas only: give 15 similar cars to {query}")
        newquer = response.text
        
        


        input_vehicles = newquer.split(",")
       

        for vehicle in input_vehicles:
            close_matches = car_data['combined'].apply(lambda x: difflib.SequenceMatcher(None, vehicle, x).ratio()).nlargest(1)
            for idx, ratio in close_matches.items():
                match = car_data.loc[idx].to_dict()
                results.append({
                    'vehicle': vehicle,
                    'brand': match['brand'],
                    'model': match['model'],
                    'year': match['year'],
                    'color': match['color'],
                    'size': match['size'],
                    'fuel': match['fuel'],
                    'score': ratio
                })
          
        return jsonify(results)

        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)