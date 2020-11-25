from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from allocation import config
from allocation.domain import model
from allocation.adapters import orm, repository
from allocation.service_layer import services, unit_of_work

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)

@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    orderid, sku, qty = request.json['orderid'], request.json['sku'], request.json['qty']
    try:
        batchref = services.allocate(orderid, sku, qty, unit_of_work.SqlAlchemyUnitOfWork())
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400
        
    session.commit()
    return jsonify({'batchref': batchref}), 201

@app.route("/add_batch", methods=["POST"])
def add_batch():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"], request.json["sku"], request.json["qty"], eta, unit_of_work.SqlAlchemyUnitOfWork()
    )
    return "OK", 201