"""A module for parsing tcx file into a list of activities."""
import datetime
import itertools
import xmltodict


__version__ = '0.1.0'


class Point(object):  # pylint: disable=too-few-public-methods
    """Represents a point in space-time.  Also includes TCX information such
    as heart rate and cadence."""
    def __init__(self, trackpoint):
        self.time = datetime.datetime.strptime(
            trackpoint['Time'], '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        self.latitude = float(trackpoint['Position']['LatitudeDegrees'])
        self.longitude = float(trackpoint['Position']['LongitudeDegrees'])
        self.altitude = float(trackpoint['AltitudeMeters'])
        heart_rate = trackpoint.get('HeartRateBpm', {}).get('Value')
        if heart_rate is None:
            self.heart_rate = heart_rate
        else:
            self.heart_rate = float(heart_rate)
        self.cadence = float(trackpoint['Extensions']['TPX']['RunCadence'])


class Lap(object):
    """Represents a "lap".  Not necessarily round a course, but a section of a
    longer activity.  Frequently around 1 km or 1 mile depending on the user's
    settings."""
    def __init__(self, track):
        self.points = [Point(point) for point in track['Track']['Trackpoint']]

    def start(self):
        """Returns the first recorded time for the lap."""
        return self.points[0].time

    def stop(self):
        """Returns the last recorded time for the lap."""
        return self.points[-1].time


class Activity(object):
    """Represents a recorded activity.  An activity consistens of a number of
    laps, each with a number of points and in total records an entire
    workout."""
    def __init__(self, activity):
        self.laps = [Lap(lap) for lap in activity['Lap']]
        self.name = activity['Notes']
        self.sport = activity['@Sport']

    def start(self):
        """Returns the first recorded time for the activity."""
        return self.laps[0].start()

    def stop(self):
        """Returns the last recorded time for the activity."""
        return self.laps[-1].stop()

    def points(self):
        """Returns an iterator with all the points for the activity."""
        return itertools.chain(*[x.points for x in self.laps])


def parse_to_activities(text):
    """Parses the text from a TCX file into a list of activities."""
    data = xmltodict.parse(text)
    activity_data = data['TrainingCenterDatabase']['Activities']['Activity']
    if isinstance(activity_data, dict):
        activity_data = [activity_data]
    activities = [Activity(x) for x in activity_data]
    return activities
