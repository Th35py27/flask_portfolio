import json, jwt
from flask import Blueprint, request, jsonify, current_app, Response
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
from auth_middleware import token_required
import random
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from model.users import User
import sqlite3

stats_api = Blueprint('stats_api', __name__,
                   url_prefix='/api/stats')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(stats_api)

class Statistics(Resource):
    def post(self):
        data = request.json['data']
        analysis_type = request.json['analysis_type']
        df = pd.DataFrame(data)

        if analysis_type == 'summary_statistics':
            summary_stats = df.describe().to_dict()
            return jsonify({
                'summary_statistics': summary_stats
            })
        elif analysis_type == 'linear_regression':
            X = np.array(df.iloc[:, :-1])
            y = np.array(df.iloc[:, -1])
            model = LinearRegression()
            model.fit(X, y)
            coefficients = model.coef_.tolist()
            intercept = model.intercept_.tolist()
            regression_line = model.predict(X).tolist()
            
            return jsonify({
                'linear_regression': {
                    'coefficients': coefficients,
                    'intercept': intercept,
                    'regression_line': regression_line,
                    'data_points': y.tolist(),
                    'features': X.tolist()
                }
            })
        elif analysis_type == 'box_plot':
            box_plot_data = df.to_dict(orient='list')
            return jsonify({
                'box_plot': box_plot_data
            })
        else:
            return jsonify({'error': 'Invalid analysis type'})

class SortData(Resource):
    def post(self):
        data = request.json['data']
        column = request.json['column']
        ascending = request.json.get('ascending', True)
        df = pd.DataFrame(data)

        sorted_df = df.sort_values(by=column, ascending=ascending)
        sorted_data = sorted_df.to_dict(orient='records')

        return jsonify({'sorted_data': sorted_data})

class SearchData(Resource):
    def post(self):
        data = request.json['data']
        column = request.json['column']
        value = request.json['value']
        df = pd.DataFrame(data)

        searched_df = df[df[column] == value]
        searched_data = searched_df.to_dict(orient='records')

        return jsonify({'searched_data': searched_data})

api.add_resource(Statistics, '/statistics')
api.add_resource(SortData, '/sort-data')
api.add_resource(SearchData, '/search-data')

