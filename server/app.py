#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b"Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


def paywall(f):
    
    def decorated(*args, **kwargs):
        session["page_views"] = 0 if "page_views" not in session else session["page_views"]

        id = kwargs.get("id")
        if id not in session.get("viewed_articles", []):
            session.setdefault("viewed_articles", []).append(id)
        session["viewed_count"] = session.get("viewed_count", 0) + 1
        session["page_views"] += 1

        if session.get("viewed_count", 0) > 3:
            return {"message": "Maximum pageview limit reached"}, 401

        return f(*args, **kwargs)

    return decorated


class ArticleResource(Resource):
    method_decorators = [paywall]

    def get(self, id):
        if (article := db.session.get(Article, id)) is None:
            return {"message": "Article not found."}, 404

        return article.to_dict(), 200


api.add_resource(ArticleResource, "/articles/<int:id>")


@app.route("/clear")
def clear_session():
    session["page_views"] = 0
    return {"message": "200: Successfully cleared session data."}, 200


@app.route("/articles/<int:id>")
def show_article(id):

    pass


if __name__ == "__main__":
    app.run(port=5555)
