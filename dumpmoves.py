#!/usr/bin/env python
from flask import Flask, url_for, request, session, redirect
from moves import MovesClient
from datetime import datetime, timedelta, date
from itertools import groupby
from operator import itemgetter
import thread
import sys
import time
import urllib
import shelve


class TokenReceiver(object):

    def __init__(self, port, moves, key):
        self.app = Flask(__name__)
        self.app.secret_key = key
        #self.app.debug = True
        self.port = port
        self.moves = moves

        self.token = None

    def run(self):
        @self.app.route("/")
        def index():
            oauth_return_url = url_for('oauth_return', _external=True)
            auth_url = self.moves.build_oauth_url(oauth_return_url)
            return 'Authorize this application: <a href="%s">%s</a>' % \
                (auth_url, auth_url)

        @self.app.route("/oauth_return")
        def oauth_return():
            code = request.args['code']
            oauth_return_url = url_for('oauth_return', _external=True)
            print('Received code. Requesting token.')
            self.token = self.moves.get_oauth_token(code, redirect_uri=oauth_return_url)
            print('Token received.')
            return "Hello World!"

        self.app.run(host='0.0.0.0', port=self.port)

    def wait_for_token(self, reset=False):
        if reset:
            self.token = None

        while self.token is None:
            time.sleep(0.2)

        return self.token


class BatchMovesClient(object):

    def __init__(self, client_id, client_secret, listening_port, token_cache):
        self.moves = MovesClient(client_id, client_secret)

        self.listening_port = listening_port
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_cache_file = token_cache

        self.load_token()
        self.moves.access_token = self.token

    def load_token(self):
        try:
            self.token = open(self.token_cache_file).read().strip()
        except IOError:
            self.token = None
        else:
            try:
                self.moves.user_profile(access_token=self.token)
            except OSError:
                self.token = None
                os.unlink(self.token_cache_file)

        if self.token is None:
            self.token_receiver = TokenReceiver(self.listening_port, self.moves,
                                                self.client_secret)
            thread.start_new_thread(self.token_receiver.run, ())
            self.token = self.token_receiver.wait_for_token()
            open(self.token_cache_file, 'w').write(self.token)

    def __getattr__(self, name):
        return getattr(self.moves, name)


def collect_storylines(client, cachedb):
    db = shelve.open(cachedb)

    firstdate_str = moves.user_profile()[u'profile'][u'firstDate']
    firstdate = date(int(firstdate_str[:4]), int(firstdate_str[4:6]), int(firstdate_str[6:]))

    def update_for_interval(dates):
        date_from, date_to = dates[0].strftime('%Y%m%d'), dates[-1].strftime('%Y%m%d')
        print('Getting storylines from {} to {}'.format(date_from, date_to))
        for storyline in moves.user_storyline_daily(**{'from': date_from, 'to': date_to}):
            db[str(storyline[u'date'])] = storyline

    # group unretrieved dates by up to 7 continuous days for Moves API
    date_stacked = []
    datecur = firstdate
    while datecur < date.today():
        datestr = datecur.strftime('%Y%m%d')
        if datestr not in db:
            if date_stacked and (datecur - date_stacked[0]).days >= 7:
                update_for_interval(date_stacked)
                del date_stacked[:]
            date_stacked.append(datecur)

        datecur += timedelta(days=1)

    if date_stacked:
        update_for_interval(date_stacked)


if __name__ == '__main__':
    import _keys

    moves = BatchMovesClient(_keys.client_id, _keys.client_secret, 9416, '.cached_token')
    collect_storylines(moves, 'storyline.db')

