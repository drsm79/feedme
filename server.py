from collections import Counter
from operator import attrgetter
from flask import Flask, abort, redirect, render_template
from utils import load_feeds, get_feed_content

app = Flask(__name__)
visited = []


@app.route("/favicon.ico")
def favicon():
    abort(404)


@app.route("/")
def index():
    articles = sorted(get_feed_content(load_feeds()), key=attrgetter("date"))[-50:]
    articles = [a for a in articles if a.url not in visited]
    counts = Counter()
    for a in articles:
        counts[a.feedfrom] += 1
    return render_template("feed.html", articles=articles, counts=counts)


@app.route("/<path:link>")
def visit(link):
    visited.append(link)
    return redirect(link, code=302)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response
