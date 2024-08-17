"""A module for parsing tcx file into a list of activities."""

from __future__ import annotations

import datetime
import itertools
from typing import Any, Iterator

import xmltodict

__version__ = "0.1.0"


class Point:  # pylint: disable=too-few-public-methods
    """Represents a point in space-time.  Also includes TCX information such
    as heart rate and cadence."""

    def __init__(self, trackpoint: dict[str, Any]):
        self.time = datetime.datetime.strptime(
            trackpoint["Time"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        self.latitude: float = float(trackpoint["Position"]["LatitudeDegrees"])
        self.longitude: float = float(trackpoint["Position"]["LongitudeDegrees"])
        self.altitude: float = float(trackpoint["AltitudeMeters"])
        heart_rate: str | None = trackpoint.get("HeartRateBpm", {}).get("Value")
        self.heart_rate: float | None = None
        if heart_rate is not None:
            self.heart_rate = float(heart_rate)
        self.cadence: float = float(trackpoint["Extensions"]["TPX"]["RunCadence"])


class Lap:
    """Represents a "lap".  Not necessarily round a course, but a section of a
    longer activity.  Frequently around 1 km or 1 mile depending on the user's
    settings."""

    def __init__(self, track: dict[str, dict[str, Any]]):
        self.points = [Point(point) for point in track["Track"]["Trackpoint"]]

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

    def __init__(self, activity: dict[str, Any]):
        self.laps = [Lap(lap) for lap in activity["Lap"]]
        self.name = activity["Notes"]
        self.sport = activity["@Sport"]

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
    data = xmltodict.parse(text)
    activity_data = data["TrainingCenterDatabase"]["Activities"]["Activity"]
    if isinstance(activity_data, dict):
        activity_data = [activity_data]
    activities = [Activity(x) for x in activity_data]
    return activities
