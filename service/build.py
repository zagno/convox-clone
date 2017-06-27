import os
from service.sync import SyncService

class BuildSync(SyncService):
    
    def sync(self, app):
        self.app_name = app['name']

        self._sync(
            self._compare(app)
        )

    def _sync(self, app):
        """ Export build artifact from source app and import it to the destination app """
        if not app:
            return

        self._log('Syncing build')

        active_build_id = self.source_rack.app(self.app_name).builds.active_build_id()
        tmp_file        = '/tmp/{}.tgz'.format(active_build_id)

        self.source_rack.app(self.app_name).builds.export_build(active_build_id, tmp_file)
        self.dest_rack.app(self.app_name).builds.import_build(active_build_id, tmp_file)
        os.remove(tmp_file)

        return app

    def _compare(self, app):
        """ Compare source and destination apps to see if the build id are the same or not """

        if not app:
            return

        self._log('Comparing build')

        source_build_id = self.source_rack.app(self.app_name).builds.active_build_id()

        if not source_build_id:
            return None

        #check if this build already exists on the dest rack
        dest_build = self.dest_rack.app(self.app_name).builds.get(source_build_id)

        if dest_build and 'error' not in dest_build:
            self._log('Build {} exists'.format(source_build_id))

            return None

        self._log('Build {} not found'.format(source_build_id))

        return app
