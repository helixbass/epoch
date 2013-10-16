import app as ap
from flask import url_for
from pytest import fixture, raises, mark
import re

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
    assert '<li>' not in app.get('/orders').data

class TestOrder(object):
    @fixture(autouse=True)
    def created_order_id(self, app):
        resp = app.post('/orders', data={ 'name': 'Test Order' })
        return re.search(r'''href=.+/([^/]+)['"]''', resp.data).group(1)

    def test_creates_order(self, app):
        assert '<li>' in app.get('/orders').data

    def test_initial_pending_status(self, app, created_order_id):
        assert 'pending' in app.get('/orders/%s' % created_order_id).data

    def test_update_status(self, app, created_order_id):
        app.put('/orders/%s/status' % created_order_id, data={ 'orderStatus': 'sentToLab' })
        assert 'sentToLab' in app.get('/orders/%s' % created_order_id).data

    def test_unknown_status_fails(self, app, created_order_id):
        response = app.put('/orders/%s/status' % created_order_id, data={ 'orderStatus': 'INVALID' })
        assert '400' in response.status
