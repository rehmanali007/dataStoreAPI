from flask import Flask, jsonify
from flask_restful import Api, request, Resource
from pymongo import MongoClient
import box

client = MongoClient("db", 27017)
db = client.UsersDB
registeredUsers = db.registeredUsers


app = Flask(__name__)
api = Api(app)

class Register(Resource):
    def post(self):
        if request.is_json:
            userData = box.Box(request.get_json())
            if not userData.username or not userData.password:
                res = {
                    "status_code": 200,
                    "message": "Missing arguments"
                }
                return jsonify(res)
            else:
                registeredUsers.insert_one({
                    "username": userData.username,
                    "password": userData.password,
                    "tokens": 10,
                    "sentences": {}
                })
                res = {
                    "status_code": 200,
                    "message": "You are now registered at our API."
                }
                return jsonify(res)
        else:
            res = {
                "status_code": 300,
                "message": "Please send data in json format"
            }
            return jsonify(res)



class Store(Resource):
    def post(self):
        return 200

class Get(Resource):
    def get(self):
        return 200


api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")



if __name__ == "__main__":
    app.run(host="0.0.0.0")