from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import logging
from logging.handlers import RotatingFileHandler

#init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/rest_api.log', maxBytes=10240,
                                   backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(lineno)d]'))
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('rest_api in use')
#database
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///'+ os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#init db
db = SQLAlchemy(app)

#init ma
ma = Marshmallow(app)

#Product Class/Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

#Product Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id','name','description','price','qty')

#Product Schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@app.route('/prod', methods=['POST'])
def add_product():
    try:
        name = request.json['name']
        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        qty = request.json['qty']

        new_product = Product(name, description, price, qty)

        db.session.add(new_product)
        db.session.commit()
    except Exception as error:
        app.logger.error(error)

    return product_schema.jsonify(new_product)

@app.route('/prod', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        result = products_schema.dump(products)
    except Exception as error:
        app.logger.error(error)

    return jsonify(result)

@app.route('/prod/<id>', methods=['GET'])
def get_one_product(id):
    try:
        product = Product.query.get(id)
    except Exception as error:
        app.logger.error(error)

    return product_schema.jsonify(product)

@app.route('/prod/<id>', methods=['PUT'])
def update_product(id):
    try:
        product = Product.query.get(id)

        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        qty = request.json['qty']

        product.name = name
        product.description = description
        product.price = price
        product.qty = qty

        db.session.commit()
    except Exception as error:
        app.logger.error(error)

    return product_schema.jsonify(product)

@app.route('/prod/<id>', methods=['DELETE'])
def delete_product(id):
    try:
        product = Product.query.get(id)

        db.session.delete(product)
        db.session.commit()
    except Exception as error:
        app.logger.error(error)

    return product_schema.jsonify(product)



#Run server
if __name__ == '__main__':
    app.run(debug=True)
