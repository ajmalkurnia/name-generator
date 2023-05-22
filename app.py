from model.markov import MarkovGenerator
from flask import Flask, render_template, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_assets import Bundle, Environment
from secrets import token_urlsafe

import os


app = Flask(__name__)
assets = Environment(app)
css = Bundle("src/css/*.css", output="dist/main.css")
js = Bundle("src/js/*.js", output="dist/main.js")  # new

assets.register("css", css)
assets.register("js", js)  # new
css.build()
js.build()  # new
model = MarkovGenerator.load(os.environ["MODEL_PATH"])
if "LIMITER_BYPASS_KEY" in os.environ and os.environ["LIMITER_BYPASS_KEY"]:
    key = os.environ["LIMITER_BYPASS_KEY"]
else:
    key = token_urlsafe(20)
    print(f"Auth for current session: {key}")
limiter = Limiter(
    app, key_func=get_remote_address,
    storage_uri=os.environ["LIMITER_STORAGE_URL"],
    storage_options={"connect_timeout": os.environ["LIMITER_STORAGE_TIMEOUT"]},
)


@limiter.request_filter
def header_whitelist():
    print(request.headers.get("Authorization", ""))
    return request.headers.get("Authorization", "") == key


@limiter.request_filter
def ip_whitelist():
    return request.remote_addr == "127.0.0.1" or request.remote_addr == "localhost"


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/generate', methods=["GET", "POST"])
@limiter.limit("100/minute")
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
