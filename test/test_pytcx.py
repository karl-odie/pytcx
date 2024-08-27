"""
Tests for `pygpx` module.
"""

from __future__ import annotations

import datetime
import os
from typing import Any
from xml.etree.ElementTree import Element, fromstring

import pytcx

with open(os.path.join(os.path.dirname(__file__), "Watergrove.tcx")) as h:
    WATERGROVE = h.read()


def traverse(element: Element, *args: Any) -> Any:
    for arg in args:
        element = pytcx.read_garmin_key(element, arg)
    return element


def test_first_point() -> None:
    data = fromstring(WATERGROVE)
    trackpoint = traverse(
        data,
        "Activities",
        "Activity",
        "Lap",
        "Track",
        "Trackpoint",
    )
    point = pytcx.Point(trackpoint)
    assert point.time == datetime.datetime(2017, 11, 25, 9, 2, 42, 1000)
    assert point.latitude == 53.657005447894335
    assert point.longitude == -2.131700534373522
    assert point.altitude == 241.60000610351562
    assert point.heart_rate == 108
    assert point.cadence == 0


def test_point_seven() -> None:
    data = fromstring(WATERGROVE)
    trackpoint = traverse(
        data,
        "Activities",
        "Activity",
        "Lap",
        "Track",
    ).findall(
        "garmin:Trackpoint", pytcx._GARMIN_NAMESPACE
    )[7]
    point = pytcx.Point(trackpoint)
    assert point.time == datetime.datetime(2017, 11, 25, 9, 3, 10)
    assert point.latitude == 53.657675329595804
    assert point.longitude == -2.131626270711422
    assert point.altitude == 242.8000030517578
    assert point.heart_rate is None
    assert point.cadence == 80


def test_first_lap() -> None:
    data = fromstring(WATERGROVE)
    lap_data = traverse(
        data,
        "Activities",
        "Activity",
        "Lap",
    )
    lap = pytcx.Lap(lap_data)
    assert len(lap.points) == 62
    assert [x.time for x in lap.points[0:10]] == [
        datetime.datetime(2017, 11, 25, 9, 2, 42, 1000),
        datetime.datetime(2017, 11, 25, 9, 2, 43),
        datetime.datetime(2017, 11, 25, 9, 2, 49),
        datetime.datetime(2017, 11, 25, 9, 2, 51),
        datetime.datetime(2017, 11, 25, 9, 2, 54),
        datetime.datetime(2017, 11, 25, 9, 3, 1),
        datetime.datetime(2017, 11, 25, 9, 3, 3),
        datetime.datetime(2017, 11, 25, 9, 3, 10),
        datetime.datetime(2017, 11, 25, 9, 3, 13),
        datetime.datetime(2017, 11, 25, 9, 3, 14),
    ]
    assert lap.start() == datetime.datetime(2017, 11, 25, 9, 2, 42, 1000)
    assert lap.stop() == datetime.datetime(2017, 11, 25, 9, 9, 20)


def test_activity() -> None:
    data = fromstring(WATERGROVE)
    activity_data = traverse(
        data,
        "Activities",
        "Activity",
    )
    activity = pytcx.Activity(activity_data)
    assert len(activity.laps) == 6
    assert [x.start() for x in activity.laps] == [
        datetime.datetime(2017, 11, 25, 9, 2, 42, 1000),
        datetime.datetime(2017, 11, 25, 9, 9, 23),
        datetime.datetime(2017, 11, 25, 9, 16, 39),
        datetime.datetime(2017, 11, 25, 9, 23, 57),
        datetime.datetime(2017, 11, 25, 9, 30, 10),
        datetime.datetime(2017, 11, 25, 9, 36, 6),
    ]
    assert len(list(activity.points())) == 267
    assert activity.name == "Wardle and West Littleborough Ward Running"
    assert activity.sport == "Running"
    assert activity.start() == datetime.datetime(2017, 11, 25, 9, 2, 42, 1000)
    assert activity.stop() == datetime.datetime(2017, 11, 25, 9, 36, 11)


def test_parse_text() -> None:
    activities = pytcx.parse_to_activities(WATERGROVE)
    assert len(activities) == 1
    assert activities[0].name == "Wardle and West Littleborough Ward Running"
