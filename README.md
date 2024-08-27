# pytcx

TCX parsing for Python

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

## Usage

````python
    with open('some.tcx') as h:
        text = h.read()
    activities = pytcx.parse_to_activities(text)
    for activity in activities:
        print(activity.start(), activity.name)
````


## Features

- Reads TCX files for runs synced via tapiriik
- Reads the following point data:
  - latitude
  - longitude
  - altitude
  - time
  - heart_rate
  - cadence

## Future Work

- Support cycling (need sample tcx)
- Support swimming (need sample tcx)
