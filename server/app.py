#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

# -------------------- App & DB setup --------------------

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

# -------------------- Routes --------------------

@app.route("/")
def home():
    return "<h1>Bakery GET-POST-PATCH-DELETE API</h1>"

# GET /bakeries -> list all bakeries
@app.route("/bakeries", methods=["GET"])
def bakeries():
    data = [b.to_dict() for b in Bakery.query.all()]
    return make_response(data, 200)

# GET or PATCH /bakeries/<id> -> show or update a bakery's name
@app.route("/bakeries/<int:id>", methods=["GET", "PATCH"])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if not bakery:
        return jsonify(error="Bakery not found"), 404

    if request.method == "PATCH":
        new_name = request.form.get("name")
        if new_name:
            bakery.name = new_name
            db.session.commit()

    return make_response(bakery.to_dict(), 200)

# GET /baked_goods/by_price -> baked goods sorted by price (desc)
@app.route("/baked_goods/by_price", methods=["GET"])
def baked_goods_by_price():
    goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    data = [bg.to_dict() for bg in goods]
    return make_response(data, 200)

# GET /baked_goods/most_expensive -> single most expensive baked good
@app.route("/baked_goods/most_expensive", methods=["GET"])
def most_expensive_baked_good():
    bg = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    if not bg:
        return jsonify(error="No baked goods found"), 404
    return make_response(bg.to_dict(), 200)

# POST /baked_goods -> create a baked good from form data
@app.route("/baked_goods", methods=["POST"])
def create_baked_good():
    name = request.form.get("name")
    price = request.form.get("price")
    bakery_id = request.form.get("bakery_id")

    if not name or price is None or bakery_id is None:
        return jsonify(error="name, price, and bakery_id are required"), 400

    try:
        price = float(price)
        bakery_id = int(bakery_id)
    except ValueError:
        return jsonify(error="price must be a number; bakery_id must be an integer"), 400

    bg = BakedGood(name=name, price=price, bakery_id=bakery_id)
    db.session.add(bg)
    db.session.commit()

    return make_response(bg.to_dict(), 201)

# DELETE /baked_goods/<id> -> delete a baked good
@app.route("/baked_goods/<int:id>", methods=["DELETE"])
def delete_baked_good(id):
    bg = BakedGood.query.get(id)
    if not bg:
        return jsonify(error="Baked good not found"), 404

    db.session.delete(bg)
    db.session.commit()
    return jsonify(message="Baked good deleted"), 200

# -------------------- Entrypoint --------------------

if __name__ == "__main__":
    app.run(port=5555, debug=True)
