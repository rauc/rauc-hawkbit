RAUC hawkBit Client
===================

The RAUC hawkBit client is a simple python-based application and library that
runs on your target and operates as an interface between the
`RAUC <https://github.com/rauc/rauc>`_ D-Bus API
and the `hawkBit <https://github.com/eclipse/hawkbit>`_ DDI API.

Documentation
-------------
`Read the Docs <http://rauc-hawkbit.readthedocs.io/en/latest/>`_

Contributing
------------
`Development Docs <http://rauc-hawkbit.readthedocs.io/en/latest/contributing.html>`_

Background
----------
Work on the RAUC hawkBit client started at `Pengutronix
<http://pengutronix.de/>`_ in the middle of 2016 as part of a customer's project
and for demonstration purposes. In May 2017 the decision was made to restructure
and clean up the code and publish it as Open Source software.

Quickstart
----------

Setup a configuration file

.. code-block:: cfg

  [client]
  hawkbit_server = 127.0.0.1:8080
  ssl = false
  ca_file =
  tenant_id = DEFAULT
  target_name = test-target
  auth_token = bhVahL1Il1shie2aj2poojeChee6ahShu
  mac_address = 12:34:56:78:9A:BC
  bundle_download_location = /tmp/bundle.raucb

Start the client application

.. code-block:: sh

  ./rauc-hawkbit-client -c config.cfg

Debugging
---------

When setting the log level to 'debug' the RAUC hawkBit client will print API
URLs and JSON payload sent and received. This can be done either by setting
``log_level`` from the config file

.. code-block:: cfg

  [client]
  ...
  log_level = debug

or by providing the ``-d`` (``--debug``) switch when calling the client.

.. code-block:: sh

  ./rauc-hawkbit-client -d

Copyright
---------

| Copyright (C) 2016-2017 Pengutronix, Enrico Joerns <entwicklung@pengutronix.de>
| Copyright (C) 2016-2017 Pengutronix, Bastian Stender <entwicklung@pengutronix.de>
|
| This library is free software; you can redistribute it and/or
| modify it under the terms of the GNU Lesser General Public
| License as published by the Free Software Foundation; either
| version 2.1 of the License, or (at your option) any later version.
|
| This library is distributed in the hope that it will be useful,
| but WITHOUT ANY WARRANTY; without even the implied warranty of
| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
| Lesser General Public License for more details.
|
| You should have received a copy of the GNU Lesser General Public
| License along with this library; if not, write to the Free Software
| Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
