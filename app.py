from flask import Flask, url_for, render_template, request, redirect, abort, make_response
app = Flask(__name__)

@app.route('/')
def index():
    return 'index'

class Order(object):

    stati = ('pending', 'sentToLab', 'shippedFromLab', 'receivedFromLab',
             'shipped', 'notifiedOfShipment')

    _orders = []

    @classmethod
    def all(klass):
        return klass._orders

    @classmethod
    def last(klass):
        return klass._orders[-1]

    @classmethod
    def create(klass, name):
        klass._orders.append(klass(name))

    @classmethod
    def find(klass, order_id):
        for order in klass.all():
            if order.id == order_id:
                return order
        abort(404)

    def __init__(self, name):
        try:
            self.id = self.__class__.last().id + 1
        except IndexError:
            self.id = 1
        self.name = name
        self.status = self.__class__.stati[0]

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in self.__class__.stati:
            abort(400)
        self._status = value

@app.route('/orders')
def index_orders():
    return render_template('orders.html', orders=Order.all())

@app.route('/orders', methods=['POST'])
def create_order():
    Order.create(request.form['name'])
    return make_response(render_template('order.html', order=Order.last()), 201)

@app.route('/orders/<int:order_id>')
def show_order(order_id):
    return render_template('order.html', order=Order.find(order_id))

@app.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    status = request.form.get('orderStatus')
    Order.find(order_id).status = status
    return '', 201

if __name__ == '__main__':
    app.run(debug=True)
