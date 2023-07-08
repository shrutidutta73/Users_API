from flask import Flask, jsonify
from flask_restful import Api
from pymongo import MongoClient
from API import UsersAPI, UserAPI

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017'
app.config['MONGO_DBNAME'] = 'MyDB'

client = MongoClient(app.config['MONGO_URI'])
db = client[app.config['MONGO_DBNAME']]
users_collection = db['users']
api = Api(app)

api.add_resource(UsersAPI, '/users', resource_class_kwargs={'users_collection': users_collection})
api.add_resource(UserAPI, '/user/<id>', resource_class_kwargs={'users_collection': users_collection})

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Server error'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'})

if __name__ == '__main__':
    app.run(debug=True)