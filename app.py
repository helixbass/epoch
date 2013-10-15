from flask import Flask, url_for, render_template, request, redirect
app = Flask(__name__)

@app.route('/')
def index():
    return 'index'

class Order(object):

    def __init__(self, order_id, name):
        self.id = order_id
        self.name = name

orders = [Order(0, 'John Doze')]

@app.route('/orders')
def index_orders():
    return render_template('order.html', orders=orders)

@app.route('/orders', methods=['POST'])
def create_order():
    orders.append(Order(len(orders), request.form['name']))
    return redirect(url_for('show_order', order_id=orders[-1].id))

@app.route('/orders/<int:order_id>')
def show_order(order_id):
    order = orders[order_id]
    return 'order %d: %s' % (order.id, order.name)

if __name__ == '__main__':
    app.run(debug=True)
