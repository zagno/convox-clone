import os

class BuildSync(object):
    def __init__(self, source_rack, dest_rack, logger):
        self.source_rack = source_rack
        self.dest_rack   = dest_rack
        self.logger      = logger

    def sync(self, app=None):
        self._sync(
            self._compare(app)
        )

    def _sync(self, app):
        """ Export build artifact from source app and import it to the destination app """
        if not app:
            return

        app_name = app['name']

        self.logger.info('Syncing build for {}.{}'.format(self.dest_rack.name(), app_name))

        active_build_id = self.source_rack.app(app_name).builds.active_build_id()
        tmp_file        = '/tmp/{}.tgz'.format(active_build_id)

        self.source_rack.app(app_name).builds.export_build(active_build_id, tmp_file)
        self.dest_rack.app(app_name).builds.import_build(active_build_id, tmp_file)
        os.remove(tmp_file)

        return app

    def _compare(self, app):
        """ Compare source and destination apps to see if the build id are the same or not """

        if not app:
            return

        app_name = app['name']

        self.logger.info('Comparing build for app {}'.format(app_name))

        source_build_id = self.source_rack.app(app_name).builds.active_build_id()

        if not source_build_id:
            return None

        #check if this build already exists on the dest rack
        dest_build = self.dest_rack.app(app_name).builds.get(source_build_id)

        if dest_build and 'error' not in dest_build:
            self.logger.info('Build {} exists on {}.{}'.format(
                source_build_id,
                self.dest_rack.name(),
                app_name
            ))

            return None

        self.logger.info('Build {} not found on {}.{}'.format(
            source_build_id,
            self.dest_rack.name(),
            app_name
        ))

        return app
