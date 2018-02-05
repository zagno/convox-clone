import os
from service.sync import SyncService

class FormationSync(SyncService):

    def sync(self, app, zero_out_count=False, compare_count=False):
        self.app_name = app['name']

        self._sync(
            self._compare(app, compare_count),
            zero_out_count
        )

    def _sync(self, app, zero_out_count=False):
        if not app and not zero_out_count:
            return

        source_formations = self.source_rack.app(self.app_name).formations.get()

        for source_formation in source_formations:
            self.dest_rack.app(self.app_name).formations.scale(
                process_name = source_formation['name'],
                count        = 0 if zero_out_count else source_formation['count'],
                memory       = source_formation['memory']
            )

        return

    def _compare(self, app, compare_count=False):
        """ Compare source and destination apps to see if the memory and processor count are the same or not """

        if not app:
            return

        self._log('Comparing Formation')

        source_formations = self.source_rack.app(self.app_name).formations.get()

        if not source_formations:
            return None

        dest_formations = self.dest_rack.app(self.app_name).formations.get()

        if dest_formations and 'error' in dest_formations:
            return app

        for source_formation in source_formations:
            for dest_formation in dest_formations:
                if source_formation['name'] != dest_formation['name']:
                    continue

                if compare_count and source_formation['count'] != dest_formation['count']:
                    self._log('process count mismatch')

                    return app

                if source_formation['memory'] != dest_formation['memory']:
                    self._log('memory mismatch')

                    return app

        return None
