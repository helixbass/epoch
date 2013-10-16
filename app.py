from flask import Flask, url_for, render_template, request, redirect, abort, make_response
from mongokit import Connection, Document, ValidationError as MongoValidationError
from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId
from bson.errors import InvalidId

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DATABASE = 'epoch'

class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(base64_decode(value))
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()
    def to_url(self, value):
        return base64_encode(value.binary)

app = Flask(__name__)
app.config.from_object(__name__)
try:
    app.config.from_envvar('EPOCH_CONFIG')
except RuntimeError:
    pass
app.url_map.converters['objectid'] = ObjectIDConverter

app.connection = connection = Connection(app.config['MONGODB_HOST'],
                                         app.config['MONGODB_PORT'])

@app.route('/')
def index():
    return 'index'

@connection.register
class Order(Document):

    stati = (u'pending', u'sentToLab', u'shippedFromLab', u'receivedFromLab',
             u'shipped', u'notifiedOfShipment')

    __collection__ = 'orders'
    __database__ = app.config['MONGODB_DATABASE']

    structure = {
        'name': basestring,
        'status': basestring,
    }
    required_fields = ['name', 'status']
    default_values = {
        'status': u'pending'
    }
    validators = {
        'status': lambda val: val in Order.stati
    }
    use_dot_notation = True
    def __repr__(self):
        return '<Order %r>' % self.name

    def create_from_form(self, form):
        order = self()
        order.name = form['name']
        order.save()
        return order._id

@app.route('/orders')
def index_orders():
    return render_template('orders.html', orders=connection.Order.find())

@app.route('/orders', methods=['POST'])
def create_order():
    _id = connection.Order.create_from_form(request.form)
    return redirect(url_for('show_order', order_id=_id))

@app.route('/orders/<objectid:order_id>')
def show_order(order_id):
    return render_template('order.html', order=connection.Order.find_one({'_id': order_id}))

@app.route('/orders/<objectid:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    status = request.form.get('orderStatus')
    # connection.Order.collection.update({'_id': order_id}, {'$set': {'status': status}})
    doc = connection.Order.find_one({'_id': order_id})
    doc.status = status
    try:
        doc.save()
    except MongoValidationError:
        abort(400)
    return '', 201

if __name__ == '__main__':
    app.run(debug=True)
