from flask import Flask, jsonify, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

users = [{
    'name': 'Bijay',
    'email': 'bijay@test.com',
    'role': 'developer'
}, {
    'name': 'Sumit',
    'email': 'sumit@test.com',
    'role': 'devops'
}, {
    'name': 'Abhishek',
    'email': 'abhishek@test.com',
    'role': 'tester'
}]


class AddUser(Resource):
    def post(self):
        postedData = request.get_json()
        name = postedData['name']
        email = postedData['email']
        role = postedData['role']

        newUser = {
            'name': name,
            'email': email,
            'role': role
        }

        users.append(newUser)

        return newUser


class UserList(Resource):
    def get(self):
        one_user = users[0]
        return jsonify(one_user)


@app.route('/')
def hello_world():
    return 'Hello World!'


api.add_resource(AddUser, '/addUser')
api.add_resource(UserList, '/users')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
