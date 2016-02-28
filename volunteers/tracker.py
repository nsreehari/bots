#!/usr/bin/python3

from botkey import BOTKEY, logger



import sys
import asyncio
import telepot
from telepot.async.delegate import per_from_id, create_open

"""
$ python3.4 trackera.py <token>

Tracks user actions across all flavors.
"""

class UserTracker(telepot.async.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(UserTracker, self).__init__(seed_tuple, timeout)

        # keep track of how many messages of each flavor
        self._counts = {'normal': 0,
                        'inline_query': 0,
                        'chosen_inline_result': 0}

    @asyncio.coroutine
    def on_message(self, msg):
        flavor = telepot.flavor(msg)
        self._counts[flavor] += 1

        # Display message counts separated by flavors
        print(self.id, ':',
              flavor, '+1', ':',
              ', '.join([str(self._counts[f]) for f in ['normal', 'inline_query', 'chosen_inline_result']]))

        # Have to answer inline query to receive chosen result
        if flavor == 'inline_query':
            query_id, from_id, query_string = telepot.glance(msg, flavor=flavor)

            articles = [{'type': 'article',
                             'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

            yield from self.bot.answerInlineQuery(query_id, articles)



bot = telepot.async.DelegatorBot(BOTKEY, [
    (per_from_id(), create_open(UserTracker, timeout=20)),
])
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()


