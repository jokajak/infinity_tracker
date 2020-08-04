.. Carrier Infinity Management documentation master file, created by
   sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Carrier Infinity Management's documentation!
======================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   howto
   pycharm/configuration
   users


Design
------

This web application is designed with 3 different use cases:

* Carrier Infinity Smart Thermostat Proxy Server
* Carrier Infinity HVAC Controller
* HomeAssistant HVAC service

Django Apps
```````````

* app: handles modeling an HVAC system
* proxy: handles proxying requests to/from Carrier

app
'''

This application handles modeling an HVAC system. It is responsible for synchronizing the system status to the database. This application implements the REST API to be used by HomeAssistant and the frontend.

proxy
'''''

This application handles the traffic coming from the HVAC system. It leverages models from the [app](#app) application.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
