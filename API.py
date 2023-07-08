from flask_restful import Resource, reqparse
from bson import ObjectId
from flask import jsonify

class UsersAPI(Resource):
    def __init__(self, **kwargs):
        self.users_collection = kwargs['users_collection']
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=True, help='Name is required')
        self.parser.add_argument('email', type=str, required=True, help='Email is required')
        self.parser.add_argument('password', type=str, required=True, help='Password is required')

    def get(self):
        users = self.users_collection.find()
        result = []
        if users:
            for user in users:
                result.append({'id': str(user['_id']), 'name': user['name'], 'email': user['email'], 'password': user['password']})
            return jsonify(result)
        else:
            return jsonify({'message': 'No users found'})
    
    def post(self):
        args = self.parser.parse_args()
        new_user = {'name': args['name'], 'email': args['email'], 'password': args['password']}
        existing = self.users_collection.find_one({'email': new_user['email']})

        if existing:
            return jsonify({'message': 'User already exists'})
        
        if "@" not in new_user['email']:
            return jsonify({'message': 'Invalid email'})
        if len(new_user['password']) < 8:
            return jsonify({'message': 'Password must be at least 8 characters'})

        result = self.users_collection.insert_one(new_user)
        inserted_id = str(result.inserted_id)
        new_user['_id'] = inserted_id 
        response = {'message': 'User created', 'id': inserted_id, 'name': new_user['name'], 'email': new_user['email'], 'password': new_user['password']}
        return response, 201


class UserAPI(Resource):
    def __init__(self, **kwargs):
        self.users_collection = kwargs['users_collection']
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('email', type=str)
        self.parser.add_argument('password', type=str)

    def get(self, id):
        user = self.users_collection.find_one({'_id': ObjectId(id)})
        if user:
            result = {'id': str(user['_id']), 'name': user['name'], 'email': user['email'], 'password': user['password']}
            return jsonify(result)
        else:
            return jsonify({'error': 'User not found'})
        
    def put(self, id):
        args = self.parser.parse_args()
        updated_user = {}
        if args['name']:
            updated_user['name'] = args['name']
        if args['email']:
            updated_user['email'] = args['email']
        if args['password']:
            if len(args['password']) < 8:
                return jsonify({'message': 'Password must be at least 8 characters'})
            else:
                updated_user['password'] = args['password']

        if updated_user=={}:
            return jsonify({'message': 'No fields to update'})
        
        result = self.users_collection.update_one({'_id': ObjectId(id)}, {'$set': updated_user})
        if result.matched_count > 0:
            final = self.users_collection.find_one({'_id': ObjectId(id)})
            return jsonify({'message': 'User updated', 'id': str(id), 'name': final['name'], 'email': final['email'], 'password': final['password']})
        else:
            return jsonify({'error': 'User not found'})
        
    def delete(self, id):
        user = self.users_collection.find_one({'_id': ObjectId(id)})
        if user:
            res = self.users_collection.delete_one({'_id': ObjectId(id)})
            if res.deleted_count == 1:
                return jsonify({'message': 'User deleted'})
            else:
                return jsonify({'error': 'User not found'})
        else:
            return jsonify({'error': 'User not found'})