# import required libraries and modules
import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

# import lists from data files
from data import users
from data import orders
from data import offers

# starting app
app = Flask(__name__)

# configuring app
# setting file/memory status for db
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# allow Cyrillic symbols, setting configuration parameter for encoding
app.config['JSON_AS_ASCII'] = False

# creating db instance to provide access to SQLAlchemy functions
db = SQLAlchemy(app)


# creating user class as inheritance of Model class, fields as UML

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "role": self.role,
            "phone": self.phone
        }


# creating order class as inheritance of Model class, fields as UML
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    start_date = db.Column(db.String(100))
    end_date = db.Column(db.String(100))
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "address": self.address,
            "price": self.price,
            "customer_id": self.customer_id,
            "executor_id": self.price
        }


# creating offer class as inheritance of Model class, fields as UML
class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "executor_id": self.executor_id,
        }


# creating function to add data to db
def init_db():
    # starting session
    with app.app_context():
        db.drop_all()
        db.create_all()

        # creating new users within list from file and adding to db
        for user in users.users:
            new_user = User(
                id=user["id"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                age=user["age"],
                email=user["email"],
                role=user["role"],
                phone=user["phone"]
            )
            db.session.add(new_user)

        # creating new orders within list from file and adding to db
        for order in orders.orders:
            new_order = Order(
                id=order["id"],
                name=order["name"],
                description=order["description"],
                start_date=order["start_date"],
                end_date=order["end_date"],
                address=order["address"],
                price=order["price"],
                customer_id=order["customer_id"],
                executor_id=order["executor_id"]
            )
            db.session.add(new_order)

        # creating new offers within list from file and adding to db
        for offer in offers.offers:
            new_offer = Offer(
                id=offer["id"],
                order_id=offer["order_id"],
                executor_id=offer["executor_id"]
            )
            db.session.add(new_offer)
            db.session.commit()


# creating views

# view for all users
@app.route('/users/', methods=['GET', 'POST'])
def get_users():
    """
    for 'GET': making request to each element in data list, and applying to_dict method, putting all results in the
    list, and returns as json. dumps
    for 'POST' request creating user from json from request data as class object, add new user to db, returns info
    """
    if request.method == 'GET':
        result = [user.to_dict() for user in User.query.all()]
        return json.dumps(result)
    elif request.method == 'POST':
        user_data = json.loads(request.data)
        new_user = User(
            id=user_data["id"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            age=user_data["age"],
            email=user_data["email"],
            role=user_data["role"],
            phone=user_data["phone"]
        )
        db.session.add(new_user)
        db.session.commit()
        return 'USER ADDED'


# views for one user
@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def get_user(uid):
    """
    For 'GET' request - making request to data by id, applying to_dict method, return dict
    For 'PUT' request - update fields of object with data from json of request add all data except id to db,
    returns info
    For 'DELETE' request - making request to data by id, applying a delete method to user, returns info
    """
    if request.method == 'GET':
        result = User.query.get(uid).to_dict()
        return result

    elif request.method == 'PUT':
        user_data = json.loads(request.data)
        upd_user = User.query.get(uid)
        upd_user.first_name = user_data["first_name"]
        upd_user.last_name = user_data["last_name"]
        upd_user.age = user_data["age"]
        upd_user.role = user_data["role"]
        upd_user.phone = user_data["phone"]

        db.session.add(upd_user)
        db.session.commit()
        return 'USER UPDATED'

    elif request.method == 'DELETE':

        del_user = User.query.get(uid)

        db.session.delete(del_user)
        db.session.commit()
        return 'USER DELETED'


# views for all orders
@app.route('/orders/', methods=['GET', 'POST'])
def get_orders():
    """
    for 'GET' request - making request to each element in data list, and applying to_dict method, putting all
    results in the list, and returns as json. dumps
    for 'POST' request -  creating order from json from request data as class object, add new order to db, returns info
    """
    if request.method == 'GET':
        result = [order.to_dict() for order in Order.query.all()]
        return json.dumps(result)

    elif request.method == 'POST':
        order_data = json.loads(request.data)
        new_order = Order(
            id=order_data["id"],
            name=order_data["name"],
            description=order_data["description"],
            start_date=order_data["start_date"],
            end_date=order_data["end_date"],
            address=order_data["address"],
            price=order_data["price"],
            customer_id=order_data["customer_id"],
            executor_id=order_data["executor_id"]
        )
        db.session.add(new_order)
        db.session.commit()
        return 'ORDER ADDED'


# view for one order
@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def get_order(oid):
    """
    For 'GET' request - making request to data by id, applying to_dict method, return dict
    For 'PUT' request - update fields of object with data from json of request add all data except id to db,
    returns info
    For 'DELETE' request - making request to data by id, applying a delete method to order, returns info
    """
    if request.method == 'GET':
        result = Order.query.get(oid).to_dict()
        return result

    elif request.method == 'PUT':
        order_data = json.loads(request.data)
        upd_order = Order.query.get(oid)
        upd_order.name = order_data["name"]
        upd_order.description = order_data["description"]
        upd_order.start_date = order_data["start_date"]
        upd_order.end_date = order_data["end_date"]
        upd_order.address = order_data["address"]
        upd_order.price = order_data["price"]
        upd_order.customer_id = order_data["customer_id"]
        upd_order.executor_id = order_data["executor_id"]

        db.session.add(upd_order)
        db.session.commit()
        return 'ORDER UPDATED'

    elif request.method == 'DELETE':

        del_order = Order.query.get(oid)

        db.session.delete(del_order)
        db.session.commit()
        return 'ORDER DELETED'


# view for all offers
@app.route('/offers/', methods=['GET', 'POST'])
def get_offers():
    """
    for 'GET' request - making request to each element in data list, and applying to_dict method, putting all
    results in the list, and returns as json. dumps
    for 'POST' request -  creating offer from json from request data as class object, add new offer to db, returns info
    """
    if request.method == 'GET':
        result = [offer.to_dict() for offer in Offer.query.all()]
        return json.dumps(result)

    elif request.method == 'POST':
        offer_data = json.loads(request.data)
        new_offer = Offer(
            id=offer_data["id"],
            order_id=offer_data["order_id"],
            executor_id=offer_data["executor_id"],

        )
        db.session.add(new_offer)
        db.session.commit()
        return 'OFFER ADDED'


# views for one offer
@app.route('/offers/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def get_offer(oid):
    """
    For 'GET' request - making request to data by id, applying to_dict method, return dict
    For 'PUT' request - update fields of object with data from json of request, add all data except id to db,
    returns info
    For 'DELETE' request - making request to data by id, applying a delete method to offer, returns info
    """
    if request.method == 'GET':
        result = Offer.query.get(oid).to_dict()
        return result

    elif request.method == 'PUT':
        offer_data = json.loads(request.data)
        upd_offer = Offer.query.get(oid)
        upd_offer.order_id = offer_data["order_id"]
        upd_offer.executor_id = offer_data["executor_id"]

        db.session.add(upd_offer)
        db.session.commit()
        return 'OFFER UPDATED'

    elif request.method == 'DELETE':

        del_offer = Offer.query.get(oid)

        db.session.delete(del_offer)
        db.session.commit()
        return 'USER DELETED'


if __name__ == "__main__":
    init_db()
    app.run()
