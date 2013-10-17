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

- At this point <http://localhost:5000/> should be up as the "root" of the API (which redirects to `/orders`

Running the tests
-----------------

To run the tests in `test_app.py` just run `py.test` (which should have been installed as a dependency) at the command line from the `epoch/` directory.

API endpoints
-------------

| Path                             | HTTP method | Response                                                     | Response formats | Request body formats |
| -------------------------------- | ----------- | ------------------------------------------------------------ | ---------------- | -------------------- |
| `/orders`                        | `GET`       | List of all orders, includes links to each order subresource | JSON, HTML       |                      |
| `/orders`                        | `POST`      | Redirect to newly created order                              |                  | JSON                 |
| `/orders/<order_id>`             | `GET`       | Representation of an order, including a link to update status| JSON, HTML       |                      |
| `/orders/<order_id>/status/edit` | `GET`       | Form to update an order's status                             | HTML             |                      |
| `/orders/<order_id>/status`      | `PUT`       | Redirect to order                                            |                  | JSON, HTML           |
