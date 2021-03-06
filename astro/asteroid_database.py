"""
    asteroid_database.py

    Wrapper for the astroquery JPL Horizons API
    Does all conversions and returns relevant information
"""

from astroquery.jplhorizons import Horizons

AU = 149597870.0     # conversion from AU to km
DAY2SEC = 24*60*60   # conversion from days to seconds

class AsteroidDB(object):
    """
    Grabs asteroid ephemerides from JPL Horizons database
    TODO: add orbital elements return, unit tests
    """

    def __init__(self):
        """Initialize attributes
        """
        self._step = 1           # step size
        self._step_unit = 'day'  # step size unit

    def set_step_size(self, step, step_unit):
        """
        Set step size and step size unit
        Unit options are:
        sec, min, day, hour, year

        Args:
            step (int) - step size
            step_unit (str) - unit for step size

        Returns:
            None
        """
        options = ['sec', 'min', 'day', 'hour', 'year']

        if step_unit not in options:
            raise KeyError("Invalid units. Options are: %s" % options)

        # Enforce integer step
        step = int(step)

        self._step = step
        self._step_unit = step_unit

    def get_cartesian_states(self, obj_id, epoch, end_time):
        """
        Query database and get cartesian rv
        NOTE: id requires the Horizons name, not SPK number!

        Args:
            id (str) - object ID (Horizons name)
            epoch (datetime obj) - start time
            end_time (datetime obj) - end time

        Returns:
            rv (list of rv list) - rv in the format:
                x (km), y (km), z (km), vx (km/s), vy (km/s), vz (km/s)
        """
        # Format step size for query
        if self._step_unit == 'sec':
            # Special formatting needed
            dt = int((end_time - epoch).total_seconds()/self._step)
        else:
            # Concatenate step size and unit
            dt = str(self._step)+self._step_unit[0]

        # Make call to JPL Horizons database and get data
        try:
            obj = Horizons(id=obj_id, location='@sun',
                           epochs={'start': epoch.isoformat(),
                                   'stop': end_time.isoformat(),
                                   'step': dt})
            data = obj.vectors()
        except:
            raise RuntimeError("Invalid query")

        # Get column header
        columns = data.colnames

        # Make state vectors
        rv = []
        for row in data:
            r_mult = AU          # convert AU to km
            v_mult = AU/DAY2SEC  # convert AU/day to km/s

            rv.append([row[columns.index("x")]*r_mult,
                       row[columns.index("y")]*r_mult,
                       row[columns.index("z")]*r_mult,
                       row[columns.index("vx")]*v_mult,
                       row[columns.index("vy")]*v_mult,
                       row[columns.index("vz")]*v_mult])
        return rv