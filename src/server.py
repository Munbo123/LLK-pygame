import flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import pygame


from pages.MainMenu import Main_menu

app = Flask(__name__)
CORS(app)

@app.route('/game', methods=['POST'])
def receive_data():
    # 获取请求数据
    data = request.get_json()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)