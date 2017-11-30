=============================
pytcx
=============================

.. image:: https://badge.fury.io/py/pytcx.png
    :target: http://badge.fury.io/py/pytcx

.. image:: https://travis-ci.org/heoga/pytcx.png?branch=master
    :target: https://travis-ci.org/heoga/pytcx

TCX parsing for Python

Usage
-----

.. code-block:: python

    with open('some.tcx') as h:
        text = h.read()
    activities = pytcx.parse_to_activities(text)
    for activity in activities:
        print(activity.start(), activity.name)


Features
--------

* Reads TCX files for runs synced via tapiriik
* Reads the following point data:
** latitude
** longitude
** altitude
** time
** heart_rate
** cadence

Future Work
-----------

* Support cycling (need sample tcx)
* Support swimming (need sample tcx)


