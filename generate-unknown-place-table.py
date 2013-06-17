#!/usr/bin/env python
import shelve
import csv
import sys

storylinedb = shelve.open('storyline.db', 'r')
placecategorydb = shelve.open('placecategory.db')

unknown_places = set()

for datestr, storyline in storylinedb.iteritems():
    if storyline[u'segments'] is None:
        continue

    for segment in storyline[u'segments']:
        if segment[u'type'] == u'place':
            if u'name' not in segment[u'place']:
                continue

            pname, pid = segment[u'place'][u'name'], segment[u'place'][u'id']
            if str(pid) not in placecategorydb:
                unknown_places.add((pname, pid))

w = csv.writer(sys.stdout)

for pname, pid in sorted(unknown_places):
    w.writerow((pid, pname.encode('utf-8')))

