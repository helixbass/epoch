from flask import Flask, url_for, render_template, request, redirect, abort, make_response, json
from mongokit import Connection, Document, ValidationError as MongoValidationError, RequireFieldError
from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId
from bson.errors import InvalidId
from mimerender import FlaskMimeRender
from datetime import datetime
import os
from urlparse import urlparse

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DATABASE = 'epoch'

LAB_EMAIL = 'lab@example.com'

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

MONGOLAB_URI = os.environ.get('MONGOLAB_URI')
if MONGOLAB_URI:
    connection = Connection(MONGOLAB_URI)
    __database__ = urlparse(MONGOLAB_URI).path[1:]
else:
    connection = Connection(app.config['MONGODB_HOST'],
                            app.config['MONGODB_PORT'])
    __database__ = app.config['MONGODB_DATABASE']
app.connection = connection

@app.route('/')
def index():
    return redirect(url_for('index_orders'))

address_schema = {
    'street': basestring,
    'city': basestring,
    'state': basestring,
    'zip': basestring,
}

credit_card_schema = {
    'type': basestring,
    'number': basestring,
    'expires': basestring,
}

@connection.register
class Order(Document):

    stati = (u'pending', u'sentToLab', u'shippedFromLab', u'receivedFromLab',
             u'shipped', u'notifiedOfShipment')

    __collection__ = 'orders'
    __database__ = __database__

    structure = {
        'billing': {
            'name': basestring,
            'address': address_schema,
            'ccinfo': credit_card_schema,
        },
        'shipping': {
            'name': basestring,
            'address': address_schema,
            'method': basestring,
        },
        'items': [{
            'name': basestring,
            'price': int,
            'quantity': int,
        }],
        'discounts': [{
            'code': basestring,
            'amount': int,
        }],
        'lens': basestring,
        'prescription': basestring,
        'created_time': datetime,
        'status': basestring,
    }
    required_fields = ['billing.name', 'billing.address.street', 'billing.address.city',
                       'billing.address.state', 'billing.address.zip',
                       'billing.ccinfo.type', 'billing.ccinfo.number', 'billing.ccinfo.expires',
                       'shipping.name', 'shipping.address.street', 'shipping.address.city',
                       'shipping.address.state', 'shipping.address.zip', 'shipping.method',
                       'items', 'lens', 'status']
    default_values = {
        'status': u'pending',
        'lens': u'prescription',
        'created_time': datetime.utcnow
    }
    validators = {
        'status': lambda val: val in Order.stati,
        'items': lambda val: len(val)
    }
    use_dot_notation = True
    def __repr__(self):
        return '<Order %r>' % self.status

    def create_from_json(self, data):
        order = self()
        for field, value in data.items():
            order[field] = value
        try:
            order.save()
        except (MongoValidationError, RequireFieldError):
            abort(400)
        return order._id

    @staticmethod
    def from_id(_id):
        return connection.Order.find_one({'_id': _id})

mimerender = FlaskMimeRender()
class JsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return unicode(obj)
        return super(JsonEncoder, self).default(obj)
app.json_encoder = JsonEncoder
def render_json(**data):
    return json.dumps(data)

def render_html(template):
    return lambda **kwargs: render_template(template, **kwargs)

@app.route('/orders')
@mimerender(default='json',
            html=render_html('orders.html'),
            json=render_json)
def index_orders():
    query = {}
    status = request.args.get('status')
    if status:
        if status not in Order.stati:
            abort(400)
        query['status'] = status
    return {
        'orders': list(connection.Order.find(query)),
        'links': [{
            'rel': 'self',
            'title': 'Self',
            'href': url_for('index_orders', _external=True),
                  },
        ]
    }

def _email_order_details(email, order):
    pass

def _send_to_lab(order_id):
    order = Order.from_id(order_id)
    _email_order_details(app.config['LAB_EMAIL'], order)
    order.status = 'sentToLab'
    order.save()

@app.route('/orders', methods=['POST'])
def create_order():
    if request.json:
        _id = connection.Order.create_from_json(request.json)
    else:
        abort(400)
    _send_to_lab(_id)
    return redirect(url_for('show_order', order_id=_id))

@app.route('/orders/<objectid:order_id>')
@mimerender(default='json',
            html=render_html('order.html'),
            json=render_json)
def show_order(order_id):
    return {
        'order': connection.Order.from_id(order_id),
        'links': [{
            'rel': 'self',
            'title': 'Self',
            'href': url_for('show_order',
                            order_id=order_id),
                  },
                  {
            'rel': 'parent',
            'title': 'All orders',
            'href': url_for('index_orders', _external=True),
                  },
                  {
            'rel': 'updateStatus',
            'title': 'Update status',
            'href': url_for('update_order_status', order_id=order_id, _external=True)
                  }
        ]
    }

@app.route('/orders/<objectid:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    status = request.form.get('status')
    # connection.Order.collection.update({'_id': order_id}, {'$set': {'status': status}})
    doc = connection.Order.from_id(order_id)
    doc.status = status
    try:
        doc.save()
    except (MongoValidationError, RequireFieldError):
        abort(400)
    return '', 201

if __name__ == '__main__':
    app.run(debug=True)
