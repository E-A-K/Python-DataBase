import secrets
import base64
from src.database.db import DataBase
from flask_bcrypt import Bcrypt
from flask import Flask,request, jsonify


class DaneshTaban(Flask):
    def __init__(self):
        super().__init__("DaneshTaban")
        self.config["SECRET_KEY"] = secrets.token_urlsafe(32)
        self.bcrypt = Bcrypt(self)
        self.db = DataBase("json/db.json")
        self.config['auth'] = {"username": "admin", "password": "admin"}
        self.before_request(self.before_request)
        self.add_url_rule("/add_user", "add_user", self.add_user, methods=["POST"])


    

    def authenticate(self, username, password):
        if username == self.config['auth']['username'] and password == self.config['auth']['password']:
            return True
        return False
    def before_request(self):
        username,password = base64.decode(request.headers['Authorization']).encode('utf-8').split(':')
        if not self.authenticate(username, password):
            return jsonify({"error": "Authentication failed"}), 401


    def add_user(self):
        username = request.json.get("username")
        password = request.json.get("password")
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        self.db.queue_task(self.db.add_user, username, password)
        return jsonify({"message": "User added successfully"}), 201
    def remove_user(self):
        username = request.json.get("username")
        if not username:
            return jsonify({"error": "Username is required"}), 400
        self.db.queue_task(self.db.remove_user, username)
        return jsonify({"message": "User removed successfully"}), 200
    def edit_field(self):
        username = request.json.get("username")
        field = request.json.get("field")
        value = request.json.get("value")
        if not username or not field or not value:
            return jsonify({"error": "Username, field and value are required"}), 400
        self.db.queue_task(self.db.change_data, username, field, value)
        return jsonify({"message": "User data updated successfully"}), 200