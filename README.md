Moves - How do I spend a day?
=============================

This is a set of scripts to collect data and generate a plot like
[How Different Groups Spend Their Day by New York Times](http://www.nytimes.com/interactive/2009/07/31/business/20080801-metrics-graphic.html).

Requirements
------------

* [Moves Python module](https://github.com/lysol/moves)
* [Matplotlib](http://matplotlib.org/)
* [Flask](http://flask.pocoo.org/)
* [pytz](http://pytz.sourceforge.net/)
* [dateutil](http://labix.org/python-dateutil)

Installation
------------

This is not packaged for the general installation. Use just in a
working clone directory of this git repository.

Example Result
--------------

My life for last two and half months.

![Example image](https://pbs.twimg.com/media/BMx67o3CAAAecdk.jpg:large)

Usage
-----

1. Register your API client on [Moves developer site](https://dev.moves-app.com/).

2. Create __keys.py and specify client__id and client__secret like the following:

   client_id = '6QvGvRRhxHMMZHTJktQ12hI5956owtE6'
   client_secret = 'S_IzKu_i10cNOjah116AP5hMe3qqoHMbxIPBY0iUzE8lC61K2_hKFh1L9ZS3STxL'
   secret_key = 'S_IzKu_i10cNOjah116AP5hMe3qqoHMbxIPBY0iUzE8lC61K2_hKFh1L9ZS3STxL'

3. Launch `dumpmoves.py`. This listens on TCP port 9416 by default to receive code
   from OAuth procedures. Change appropriate firewall settings or the port number
   when needed.

4. Open http://your_ip_address:9416/ on a web browser, and authorize the client
   by following the presented instruction. When the authorization token is received
   by the script, it will automatically dump all your Moves storylines into
   `storyline.db` (shelve format).

5. Then, you need to classify places in your storyline into few categories.
   Generate the list of places:

   % python generate-unknown-place-table.py > my-places.csv

   Then, fill the category names on the third column with your favorite spread sheet.
   It is recommended to use category names in short single English word to make
   the subsequent processing easier.

6. When you finished filling the categorization table, run `update-place-table.py`.
   It expects CSV input from stdin, puts them into `placecategory.db` in shelve format.

   % python update-place-table.py < my-places.csv

7. Build a numeric matrix representing your daily life with `summarize-activity.py`.
   This uses the storyline database and place categorization database made in
   earlier steps.

   % python summarize-activity.py

   There are few hard-coded stuff in the script. Change them as you need. :)
   This script counts activities in regular week days. The list of holidays is
   specified in top of the script. Translation of 'moves' activity (walk, run,
   transport or cycling) to your own category name is done with `activity2category`
   dictionary on the following few lines after the list of holidays. Timezone is 
   assumed as same to the host running the script. The atomic unit of the statistics
   is defined as 300 seconds (5 minutes) on the end part of the script.

8. Plot it finally! First, change the list of activity categories and their colors
   defined inside `plot-weekdays-life.py`. Then, run the script to show the plot,
   click the save button to save the figure as a file.

   % python plot-weekdays-life.py


Disclaimer
----------

This library uses data from Moves but is not endorsed or certified by Moves. Moves is a trademark of ProtoGeo Oy.

License
-------

Copyright (c) 2013 Hyeshik Chang <hyeshik@snu.ac.kr>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
