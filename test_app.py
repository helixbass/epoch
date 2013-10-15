import app as ap
from pytest import fixture, raises

@fixture
def app():
    return ap.app.test_client()

def test_orders_initially_empty(app):
    assert '<li>' not in app.get('/orders').data

class TestOrder(object):
    @fixture(autouse=True)
    def create_order(self, app):
        app.post('/orders', data={ 'name': 'Test Order' })

    def test_creates_order(self, app):
        assert '<li>' in app.get('/orders').data

    def test_initial_pending_status(self, app):
        assert 'pending' in app.get('/orders/1').data

    def test_update_status(self, app):
        app.put('/orders/1/status', data={ 'orderStatus': 'sentToLab' })
        assert 'sentToLab' in app.get('/orders/1').data

    def test_unknown_status_fails(self, app):
        response = app.put('/orders/1/status', data={ 'orderStatus': 'INVALID' })
        assert '400' in response.status
