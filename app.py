from model.markov import MarkovGenerator
from limiter import LimitReq

from flask import Flask, render_template, jsonify, request
from flask_assets import Bundle, Environment

import os


app = Flask(__name__)
limiter = LimitReq(app)

assets = Environment(app)
css = Bundle("src/css/*.css", output="dist/main.css")
js = Bundle("src/js/*.js", output="dist/main.js")

assets.register("css", css)
assets.register("js", js)  # new
css.build()
js.build()  # new
model = MarkovGenerator.load(os.environ["MODEL_PATH"])


@limiter.flask_limit.request_filter
def header_whitelist():
    return request.headers.get("Authorization", "") == limiter.key


@limiter.flask_limit.request_filter
def ip_whitelist():
    return request.remote_addr in limiter.white_list


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/generate', methods=["GET", "POST"])
@limiter.flask_limit.limit(limiter.config)
def generate():
    if request.json:
        seed = request.json.get('seed', "")
        max_length = request.json.get('max_length', 100)
        max_words = request.json.get('max_words', 99999)
    else:
        seed = request.args.get('seed', default="", type=str)
        max_length = request.args.get('max_length', default=100, type=int)
        max_words = request.args.get('max_words', default=99999, type=int)
    name = model.generate(seed, max_length, max_words)
    return jsonify({"name": name})
