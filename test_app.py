import app as ap
from flask import url_for, json
from pytest import fixture, raises, mark
import re
from copy import deepcopy

def _json(resp):
    return json.loads(resp.data)

@fixture(scope='module')
def app(request):
    _app = ap.app
    _app.testing = True
    ctx = _app.test_request_context()
    ctx.push()
    def fin():
        ctx.pop()
    request.addfinalizer(fin)
    return _app.test_client()

@fixture
def reset_db(app):
    app.application.connection.drop_database(app.application.config['MONGODB_DATABASE'])

@mark.usefixtures('reset_db')
def test_orders_initially_empty(app):
    assert len(_json(app.get('/orders'))['orders']) == 0

def _bad(response):
    assert '400' in response.status

def test_invalid_status_query(app):
    _bad(app.get('/orders?status=INVALID_STATUS'))

valid_order_data = {
    'billing': {
        'name': 'John Doze Jr.',
        'address': {
            'street': '123 Pleasant Rd.',
            'city': 'Someville',
            'state': 'MA',
            'zip': '12345'
        },
        'ccinfo': {
            'type': 'Visa',
            'number': '1111222233334444',
            'expires': '10/2020',
        },
    },
    'shipping': {
        'name': 'Joan Doze',
        'address': {
            'street': '123 Pleasant Rd.',
            'city': 'Someville',
            'state': 'MA',
            'zip': '12345'
        },
        'method': 'UPS Ground',
    },
    'items': [{
        'name': 'classic',
        'price': 7500,
        'quantity': 1,
    }],
    'discounts': [{
        'code': '10OFF',
        'amount': 10,
    }],
    'lens': 'prescription',
    'prescription': '4.5/3.5',
}

def _post_order(data, app):
    return app.post('/orders', data=json.dumps(data), headers={ 'Content-type': 'application/json' })

class TestOrder(object):

    @fixture(autouse=True)
    def created_order_id(self, app):
        resp = _post_order(valid_order_data, app)
        return re.search(r'''href=.+/([^/]+)['"]''', resp.data).group(1)

    def test_creates_order(self, app):
        assert len(_json(app.get('/orders'))['orders']) == 1

    def test_initial_sentToLab_status(self, app, created_order_id):
        assert 'sentToLab' in app.get('/orders/%s' % created_order_id).data

    def test_update_status(self, app, created_order_id):
        app.put('/orders/%s/status' % created_order_id, data={ 'status': 'sentToLab' })
        assert 'sentToLab' in app.get('/orders/%s' % created_order_id).data

    def test_unknown_status_fails(self, app, created_order_id):
        _bad(app.put('/orders/%s/status' % created_order_id, data={ 'status': 'INVALID' }))

class TestMalformedOrders(object):

    def test_no_items(self, app):
        _bad(_post_order(dict(valid_order_data, items=[]), app))

    def test_no_shipping_address(self, app):
        data = deepcopy(valid_order_data)
        del data['shipping']['address']
        _bad(_post_order(data, app))
