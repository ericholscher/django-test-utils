import logging

from django.conf import settings
from django.db import connections

from base import Plugin

LOG = logging.getLogger('crawler')

class QueryCount(Plugin):
    """
    Report the number of queries used to serve a page
    """

    def __init__(self):
        super(QueryCount, self).__init__()
        self.query_counts = self.data['query_counts'] = {}

        # Horrible monkey-patch to log query counts when DEBUG = False:
        for conn in connections.all():
            conn.dtu_query_count = 0
            self._monkey_cursor_execute(conn)

    def _monkey_cursor_execute(self, conn):
            old_cursor = conn.cursor
            def new_cursor(*args, **kwargs):
                c = old_cursor(*args, **kwargs)

                old_execute = c.execute
                def new_execute(*args, **kwargs):
                    try:
                        return old_execute(*args, **kwargs)
                    finally:
                            conn.dtu_query_count += 1
                c.execute = new_execute

                old_executemany = c.executemany
                def new_executemany(s, sql, param_list, *args, **kwargs):
                    try:
                        return old_executemany(s, sql, param_list, *args, **kwargs)
                    finally:
                            conn.dtu_query_count += len(param_list)
                c.executemany = new_executemany

                return c

            conn.cursor = new_cursor

    def pre_request(self, sender, **kwargs):
        url = kwargs['url']
        self.query_counts[url] = dict((c.alias, c.dtu_query_count) for c in connections.all())

    def post_request(self, sender, **kwargs):
        url = kwargs['url']

        new_query_counts = [(c.alias, c.dtu_query_count) for c in connections.all()]

        deltas = {}
        for k, v in new_query_counts:
            # Skip inactive connections:
            if v > 0:
                deltas[k] = v - self.query_counts[url][k]

        for k, v in sorted(deltas.items(), reverse=True):
            if v > 50:
                log_f = LOG.critical
            elif v > 20:
                log_f = LOG.error
            elif v > 10:
                log_f = LOG.warning
            else:
                log_f = LOG.info
            log_f("%s: %s %d queries", url, k, v)

PLUGIN = QueryCount