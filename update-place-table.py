#!/usr/bin/env python
import csv
import shelve
import sys

placedb = shelve.open('placecategory.db')

for row in csv.reader(sys.stdin):
    placedb[row[0]] = row[2]

placedb.sync()

