from flask import Flask, jsonify
from flask_restful import Api, request, Resource
from pymongo import MongoClient
import box
import bcrypt


client = MongoClient("db", 27017)
db = client.UsersDB
registeredUsers = db.registeredUsers


app = Flask(__name__)
api = Api(app)


def validUser(username, password):
    foundUser = box.Box(registeredUsers.find_one({"username": username}))
    if foundUser:
        if bcrypt.checkpw(password.encode('utf8'), foundUser.password):
            return True
        else:
            return False
    else:
        return False


def getToken(username):
    user = box.Box(registeredUsers.find_one({"username": username}))
    return user.tokens


def setTokens(username, newTokens):
    registeredUsers.update_one({"username": username},
                               {"$set": {"tokens": newTokens}})


class Register(Resource):
    def post(self):
        if request.is_json:
            userData = box.Box(request.get_json())
            if not userData.username or not userData.password:
                res = {
                    "status_code": 200,
                    "message": "Missing Username/Password field!"
                }
                return jsonify(res)
            else:
                hashed_pw = bcrypt.hashpw(userData.password.encode('utf8'),
                                          bcrypt.gensalt())
                registeredUsers.insert_one({
                    "username": userData.username,
                    "password": hashed_pw,
                    "tokens": 10,
                    "sentence": ""
                })
                res = {
                    "status_code": 200,
                    "message": "You are now registered at our API.",
                    "tokens": 10
                }
                return jsonify(res)
        else:
            res = {
                "status_code": 300,
                "message": "Please send data in json format."
            }
            return jsonify(res)


class Store(Resource):
    def post(self):
        if request.is_json:
            userData = box.Box(request.get_json())
            if not userData.username or not userData.password:
                res = {
                    "status_code": 200,
                    "message": "Missing Username/Password field!"
                }
                return jsonify(res)
            if validUser(userData.username, userData.password):
                tokens = getToken(userData.username)
                if tokens > 0:
                    registeredUsers.update_one({
                        "username": userData.username
                    }, {"$set": {"sentence": userData.sentence}})
                    tokens -= 1
                    setTokens(userData.username, tokens)
                    res = {
                        "status_code": 200,
                        "message": "Successfully saved your sentence to db.",
                        "tokens": tokens
                    }
                    return jsonify(res)
                else:
                    res = {
                        "status_code": 302,
                        "message": "Not enough tokens!"
                    }
                    return jsonify(res)
            else:
                res = {
                    "status_code": 404,
                    "message": "User does'nt exist in our databases."
                }
                return jsonify(res)
        else:
            res = {
                "status_code": 300,
                "message": "Please send data in json format."
            }
            return jsonify(res)


class Get(Resource):
    def post(self):
        if request.is_json:
            userData = box.Box(request.get_json())
            if not userData.username or not userData.password:
                res = {
                    "status_code": 200,
                    "message": "Missing Username/Password field!"
                }
                return jsonify(res)

            if validUser(userData.username, userData.password):
                tokens = getToken(userData.username)
                if tokens > 0:
                    foundUser = box.Box(registeredUsers.find_one({
                        "username": userData.username}))
                    if foundUser:
                        tokens -= 1
                        setTokens(foundUser.username, tokens)
                        res = {
                            "status_code": 200,
                            "sentence": foundUser.sentence,
                            "tokens": foundUser.tokens
                        }
                        return jsonify(res)
                else:
                    res = {
                        "status_code": 302,
                        "message": "Not enough tokens!"
                    }
                    return jsonify(res)
            else:
                res = {
                    "status_code": 404,
                    "message": "User does'nt exist in our databases."
                }
                return jsonify(res)
        else:
            res = {
                "status_code": 300,
                "message": "Please send data in json format."
            }
            return jsonify(res)


api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
