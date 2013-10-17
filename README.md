Prerequisites
-------------
Requires MongoDB to be installed & running

Installing the app
------------------

- Clone the `helixbass/epoch` Github repository

- Create & activate a python virtualenv

- Install the project's dependencies using e.g.:

        $ cd epoch
        $ pip install -e .

Configuring the app
-------------------

If MongoDB is running somewhere other than `localhost:27017` you can override `MONGODB_HOST` and/or `MONGODB_PORT` by either:
  1. editing `app.py` directly OR
  2. creating a config file (e.g. `local.cfg`) which sets `MONGODB_HOST`/`MONGODB_PORT` correctly, and then referencing that config file in the environment variable `EPOCH_CONFIG` when you run the app, e.g.:

        $ cd epoch
        $ cat local.cfg
        MONGODB_HOST = 'mongo.example.com'
        MONGODB_PORT = 12345
        $ EPOCH_CONFIG=local.cfg python app.py

You can also similarly override `MONGODB_DATABASE` if you don't want to use the default (`epoch`)

Running the app
---------------

- To run locally using Flask's builtin webserver:

        $ python app.py

- At this point <http://localhost:5000/> should be up as the "root" of the API (which redirects to `/orders`)

Running the tests
-----------------

The test suite (in `test_app.py`) uses `py.test`, which should have been installed (into the virtualenv) as a dependency. To run the tests:

    $ cd epoch
    $ EPOCH_CONFIG=test.cfg py.test

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
