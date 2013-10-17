Prerequisites
-------------
Requires MongoDB to be installed & running

Running the app
---------------

- Clone the `helixbass/epoch` Github repository

- Create & activate a python virtualenv

- Install the project's dependencies using e.g.:

        $ cd epoch
        $ pip install -e .

- To run locally using Flask's builtin webserver:

        $ ./app.py

- At this point <http://localhost:5000/> should be up as the "root" of the API (which redirects to `/orders`)

Running the tests
-----------------

The test suite (in `test_app.py`) uses `py.test`, which should have been installed (into the virtualenv) as a dependency. To run the tests:

    $ cd epoch
    $ py.test

API endpoints
-------------

| Path                             | HTTP method | Response                                                     | Response formats | Request body formats |
| -------------------------------- | ----------- | ------------------------------------------------------------ | ---------------- | -------------------- |
| `/orders`                        | `GET`       | List of all orders, includes links to each order subresource | JSON, HTML       |                      |
| `/orders?status=<status>`        | `GET`       | List of all orders whose current status is `<status>`        | JSON, HTML       |                      |
| `/orders`                        | `POST`      | Redirect to newly created order                              |                  | JSON                 |
| `/orders/<order_id>`             | `GET`       | Representation of an order, including a link to update status| JSON, HTML       |                      |
| `/orders/<order_id>/status/edit` | `GET`       | Form to update an order's status                             | HTML             |                      |
| `/orders/<order_id>/status`      | `PUT`       | Redirect to order                                            |                  | JSON, HTML           |

Creating orders
---------------

There is no HTML form to create a new order, you must send JSON, e.g. the `valid_order_data` from the tests:

    $ cd epoch
    $ python
    >>> import requests
    >>> from flask import json
    >>> from test_app import valid_order_data
    >>> requests.post( 'http://localhost:5000/orders', data=json.dumps(valid_order_data), headers={'Content-type': 'application/json'})
