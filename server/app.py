from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})

# for connecting to local mongo db
# app.config['MONGO_URI'] = "mongodb://localhost:27017/flaskUsers"

# for connecting to k8s pod running mongo container
app.config['MONGO_URI'] = "mongodb://flask-mongo-srvc:27017/flaskUsers"

mongo = PyMongo(app)

allUsers = [{
    'name': 'Bijay',
    'email': 'bijay@test.com',
    'role': 'admin',
    'password': 'test@123',
    'designation': 'Developer'
}, {
    "name": "Sumit",
    "email": "sumit@test.com",
    "role": "user",
    "password": "test@123",
    "designation": "devops"
}, {
    "name": "Abhishek",
    "email": "abhishek@test.com",
    "role": "user",
    "password": "test@123",
    "designation": "tester"
}]


# Populate DB with data
@app.route('/')
def populate_users():
    for userD in allUsers:
        for data in userD:
            if data == 'password':
                userD[data] = generate_password_hash(userD[data])

    for userD in allUsers:
        userExists = mongo.db.users.find_one({'email': userD['email']})
        if not userExists:
            mongo.db.users.insert(userD)

    return 'User data populated successfully'


# Adding new user to DB
@app.route('/addUser', methods=['POST'])
def add_user():
    _jsonData = request.json
    _name = _jsonData['name']
    _email = _jsonData['email']
    _role = _jsonData['role']
    _password = _jsonData['password']
    _designation = _jsonData['designation']

    if _name and _email and _role and _password and _designation and request.method == 'POST':
        _hashed_password = generate_password_hash(_password)
        userObj = {
            'name': _name,
            'email': _email,
            'role': _role,
            'password': _hashed_password,
            'designation': _designation
        }

        mongo.db.users.insert(userObj)

        res = dumps({
            'message': 'User created successfully',
            'user': userObj
        })

        return res, 201
    else:
        return not_found()


# Fetching users from DB
@app.route('/users')
def users():
    retrievedUsers = mongo.db.users.find()
    res = dumps(retrievedUsers)
    return res, 200


# Logging in a User
@app.route('/login', methods=['POST'])
def user_login():
    _jsonData = request.json
    _email = _jsonData['email']
    _password = _jsonData['password']
    retrievedUser = mongo.db.users.find_one({'email': _email})
    if not retrievedUser:
        message = "Invalid user details"
        return jsonify(message), 400
    else:
        passwordMatch = check_password_hash(retrievedUser['password'], _password)
        if passwordMatch:
            message = "User logged in successfully"
            res = dumps(retrievedUser)
            return res, 200
        else:
            message = "Invalid user details"
            return jsonify(message), 400


# Fetch a user based on id
@app.route('/users/<userId>')
def user(userId):
    retrievedUsers = mongo.db.users.find_one({'_id': ObjectId(userId)})
    res = dumps(retrievedUsers)
    return res, 200


# Delete user by id
@app.route('/users/<userId>', methods=['DELETE'])
def delete_user(userId):
    mongo.db.users.delete_one({'_id': ObjectId(userId)})
    message = f'User with id {userId} has been deleted successfully'
    res = jsonify(message)
    return res, 202


# Updating a user
@app.route('/users/<userId>', methods=['PATCH'])
def update_user(userId):
    _id = userId
    updatedUser = None

    if request.method == 'PATCH':
        mongo.db.users.update_one({'_id': ObjectId(userId)}, {'$set': request.json})
        updatedUser = mongo.db.users.find_one({'_id': ObjectId(userId)})
    else:
        return not_found()

    res = dumps({
        'message': 'User updated successfully',
        'user': updatedUser
    })

    return res, 200


# For 404 not found errors
@app.errorhandler(404)
def not_found(error=None):
    message = 'Not found ' + request.url
    res = jsonify(message)
    return res, 404


if __name__ == '__main__':
    app.run(host='0.0.0.0')
