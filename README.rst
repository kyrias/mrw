=====
 mrw
=====
---------------
 My Remote Who
---------------

mrw is an attempt at writing an implementation of a centralized ``who`` system, inspired by `@grawity`_'s _rwho, in python.

The server component uses flask to serve the API, HTTP Basic Auth for the authentication, and msgpack for the content submitted to it, though it is easy to add other over-the-wirte formats.

The agent component currently only works on Linux due to using inotify to look for changes to the utmp file.
It uses the ``utmp`` python module to read the utmp file, and ``msgpack-python`` and ``requests`` to send a ``PUT`` request to the server.

.. _`@grawity`: https://nullroute.eu.org/~grawity/
.. _`rwho`: https://github.com/grawity/rwho/

License
=======

All of the files contained in this repository are licensed under the ISC license.
See the ``LICENSE`` file for the full license text.
