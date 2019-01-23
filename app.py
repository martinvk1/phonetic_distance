from flask import Flask, render_template, flash, request, jsonify, abort
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import traceback
import re
import os
import g2p_en as g2p
import ast
import time

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
API_KEY = os.environ.get('API_KEY') or "QITumvVBxGI7F4GDLRPiaiqdEEgzOktEJOXVkPX8"


def headline_choice(headlines, query):
    
    def levenshtein(s1, s2):
        if len(s1) < len(s2):
            return levenshtein(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
    
    with g2p.Session():
        search_query = ''.join([phoneme[:2] for phoneme in g2p.g2p(query) if phoneme != ' '])
        headlines = [''.join([phoneme[:2] for phoneme in g2p.g2p(text) if phoneme != ' ']) for text in headlines]
     
    chosen_index = 0
    min_distance = len(query)
    query = search_query
    for index, t in enumerate(headlines):
        edit_distances = []
        if len(query) > len(t):
            t, query = query, t
        if len(query) == len(t):
            t += ' '
        for i in range(0, len(t) - len(query), 1):
            substring = t[i:i+len(query)]
            edit_distances.append(levenshtein(query, substring))
        if min(edit_distances) < min_distance:
            min_distance = min(edit_distances)
            chosen_index = index
        query = search_query
                
    return chosen_index


class ReusableForm(Form):
	name = TextField('Search query:', validators=[validators.required()])


@app.route('/api/g2p', methods=['GET', 'POST'])
def api_g2p():
    try:
        if request.args.get('api_key') != API_KEY:
        	print(request.args.get('api_key'))
        	abort(401)
        query = request.args.get('query')
        headlines = ast.literal_eval(request.args.get('headlines'))
        print(len(headlines))
        tic = time.time()
        choice = headline_choice(headlines,query)
        toc = time.time()
        return jsonify({'index': choice, 'time': toc - tic})

    except Exception:
        print("Could not perform search")
        print(traceback.format_exc())
        return jsonify({'error': traceback.format_exc()})

if __name__ == "__main__":
	app.run()