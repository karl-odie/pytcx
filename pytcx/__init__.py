"""A module for parsing tcx file into a list of activities."""

from __future__ import annotations

import datetime
import itertools
from typing import TYPE_CHECKING, Iterator

from defusedxml import ElementTree

if TYPE_CHECKING:
    # Used for typing, defusedxml used for code.
    from xml.etree.ElementTree import Element  # nosec: B405

__version__ = "0.1.0"

_GARMIN_NAMESPACE = {
    "garmin": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2",
    "tpx": "http://www.garmin.com/xmlschemas/ActivityExtension/v2",
}


class TCXParseException(Exception):
    """Exception encountered parsing TCX structure."""


def read_garmin_key(element: Element, key: str) -> Element:
    child = element.find(f"garmin:{key}", _GARMIN_NAMESPACE)
    if child is None:
        raise TCXParseException(f"{element.tag} contains no {key}")
    return child


def read_garmin_key_text(element: Element, key: str) -> str:
    child = element.find(f"garmin:{key}", _GARMIN_NAMESPACE)
    if child is None:
        raise TCXParseException(f"{element.tag} contains no {key}")
    text = child.text
    if text is None:
        raise TCXParseException(f"{key} has no text")
    return text


def read_tpx_key(element: Element, key: str) -> Element:
    child = element.find(f"tpx:{key}", _GARMIN_NAMESPACE)
    if child is None:
        raise TCXParseException(f"{element.tag} contains no {key}")
    return child


def read_tpx_key_text(element: Element, key: str) -> str:
    child = element.find(f"tpx:{key}", _GARMIN_NAMESPACE)
    if child is None:
        raise TCXParseException(f"{element.tag} contains no {key}")
    text = child.text
    if text is None:
        raise TCXParseException(f"{key} has no text")
    return text


class Point:  # pylint: disable=too-few-public-methods
    """Represents a point in space-time.  Also includes TCX information such
    as heart rate and cadence."""

    def __init__(self, element: Element):  #
        position = read_garmin_key(element, "Position")
        self.time = datetime.datetime.strptime(
            read_garmin_key_text(element, "Time"), "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        self.latitude: float = float(read_garmin_key_text(position, "LatitudeDegrees"))
        self.longitude: float = float(
            read_garmin_key_text(position, "LongitudeDegrees")
        )
        self.altitude: float = float(read_garmin_key_text(element, "AltitudeMeters"))

        self.heart_rate: float | None = None
        try:
            heart_rate_bpm = read_garmin_key(element, "HeartRateBpm")
        except TCXParseException:
            pass
        else:
            heart_rate_bpm_value = read_garmin_key(heart_rate_bpm, "Value")
            self.heart_rate = float(heart_rate_bpm_value.text)

        self.cadence: float | None = None
        try:
            extensions = read_garmin_key(element, "Extensions")
            tpx = read_tpx_key(extensions, "TPX")
            cadence = read_tpx_key_text(tpx, "RunCadence")
            self.cadence: float = float(cadence)
        except TCXParseException:
            pass


class Lap:
    """Represents a "lap".  Not necessarily round a course, but a section of a
    longer activity.  Frequently around 1 km or 1 mile depending on the user's
    settings."""

    def __init__(self, element: Element):
        track = read_garmin_key(element, "Track")
        trackpoints = track.findall("garmin:Trackpoint", _GARMIN_NAMESPACE)
        self.points = [Point(point) for point in trackpoints]

    def start(self) -> datetime.datetime:
        """Returns the first recorded time for the lap."""
        return self.points[0].time

    def stop(self) -> datetime.datetime:
        """Returns the last recorded time for the lap."""
        return self.points[-1].time


class Activity:
    """Represents a recorded activity.  An activity consistens of a number of
    laps, each with a number of points and in total records an entire
    workout."""

    def __init__(self, activity: Element):
        laps = activity.findall("garmin:Lap", _GARMIN_NAMESPACE)
        notes = read_garmin_key(activity, "Notes")
        self.name = notes.text
        self.sport = activity.attrib["Sport"]
        self.laps = [Lap(lap) for lap in laps]

    def start(self) -> datetime.datetime:
        """Returns the first recorded time for the activity."""
        return self.laps[0].start()

    def stop(self) -> datetime.datetime:
        """Returns the last recorded time for the activity."""
        return self.laps[-1].stop()

    def points(self) -> Iterator[Point]:
        """Returns an iterator with all the points for the activity."""
        return itertools.chain(*[x.points for x in self.laps])


def parse_to_activities(text: str) -> list[Activity]:
    """Parses the text from a TCX file into a list of activities."""

    root = ElementTree.fromstring(text, forbid_dtd=True)
    activities_elements = root.findall("garmin:Activities", _GARMIN_NAMESPACE)
    activities: list[Activity] = []
    for element in activities_elements:
        activities = [
            Activity(x) for x in element.findall("garmin:Activity", _GARMIN_NAMESPACE)
        ]
    return activities
