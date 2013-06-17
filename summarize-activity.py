#!/usr/bin/env python
from __future__ import division
import numpy as np
from datetime import datetime, date
from dateutil import parser
from collections import defaultdict
import math
import time
import calendar
import shelve
import pickle

holidays = set([
    (2013, 5, 17), # Buddha's birthday
    (2013, 5, 18), # oops?
    (2013, 6, 6), # Memorial day
])

placedb = shelve.open('placecategory.db', 'r')
storylinedb = shelve.open('storyline.db', 'r')
activity2category = {
    'trp': 'transport',
    'wlk': 'walk',
    'run': 'walk',
}

def digest_storyline():
    for storyline in storylinedb.itervalues():
        if storyline[u'segments'] is None:
            continue

        for segment in storyline[u'segments']:

            if segment[u'type'] == u'move':
                for activity in segment.get(u'activities', []):
                    startTime = parser.parse(activity[u'startTime'])
                    endTime = parser.parse(activity[u'endTime'])
                    category = activity2category[activity[u'activity']]
                    yield (category, startTime, endTime)
            elif segment[u'type'] == u'place':
                startTime = parser.parse(segment[u'startTime'])
                endTime = parser.parse(segment[u'endTime'])

                try:
                    category = placedb[str(segment[u'place'][u'id'])]
                except KeyError:
                    # unnamed place found. uncomment this block if you want to fix them.
#                    if (endTime - startTime).total_seconds() > 300:
#                        import pytz
#                        print '=============='
#                        print startTime.astimezone(pytz.timezone('Asia/Tokyo'))
#                        pprint.pprint(segment)
#                        raise
                    pass
                else:
                    yield (category, startTime, endTime)
            else:
                raise ValueError('Unknown type of segment: ' + segment[u'type'])


class TimeBlocksCounter(object):

    def __init__(self, timeunit, timezone):
        self.timeunit = timeunit
        self.timezone = timezone
        self.timeunit_a_day = 24 * 60 * 60 / timeunit
        self.blocks = defaultdict(lambda: defaultdict(float))

    def divide_time(self, start, end):
        start_ts = calendar.timegm(start.timetuple())
        end_ts = calendar.timegm(end.timetuple())

        secondblkstart = math.ceil(start_ts / self.timeunit) * self.timeunit
        if secondblkstart >= end_ts:
            yield (start_ts, end_ts)
            return

        yield (start_ts, secondblkstart)
        for blkstart in np.arange(secondblkstart, end_ts, self.timeunit):
            yield (blkstart, min(end_ts, blkstart + self.timeunit))

    def update(self, starttime, endtime, activity):
        for blkstart, blkend in self.divide_time(starttime, endtime):
            if not self.is_weekday(blkstart):
                continue
            blkno = int(int((blkstart - self.timezone) / self.timeunit) % self.timeunit_a_day)
            duration = blkend - blkstart
            self.blocks[blkno][activity] += duration

    def get_result(self):
        allactivities = set()
        result = []

        for i in range(24 * 60 * 60 // self.timeunit):
            totalsec = sum(self.blocks[i].itervalues())
            blkresult = dict((activity, sec / totalsec)
                             for activity, sec in self.blocks[i].iteritems())
            allactivities.update(set(self.blocks[i]))
            result.append((i, blkresult))

        return result, allactivities

    def is_weekday(self, ts):
        localtime = time.localtime(ts)
        return localtime.tm_wday < 5 and localtime[:3] not in holidays


if __name__ == '__main__':
    TIMEUNIT = 300

    storyline = sorted(set(digest_storyline()), key=lambda x: (x[1], x[2], x[0]))
    timecounter = TimeBlocksCounter(TIMEUNIT, time.timezone)
    for category, starttime, endtime in storyline:
        timecounter.update(starttime, endtime, category)

    pickle.dump(timecounter.get_result(), open('summarized-weekdays-life.pickle', 'w'))

