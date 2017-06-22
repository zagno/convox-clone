import os

class BuildSync(object):
    def __init__(self, source_rack, dest_rack, logger):
        self.source_rack = source_rack
        self.dest_rack   = dest_rack
        self.logger      = logger

    def sync(self, source_apps=None):
        source_apps = source_apps if source_apps else self.source_rack.apps.get()

        requiring_update = self._compare(source_apps)

        self._sync(requiring_update)

    def _sync(self, apps):
        """ Export build artifact from source app and import it to the destination app """

        for app in apps:
            app_name = app['name']

            self.logger.info('Syncing build for app {}'.format(app_name))

            active_build_id = self.source_rack.app(app_name).builds.active_build_id()
            tmp_file        = '/tmp/{}.tgz'.format(active_build_id)

            self.source_rack.app(app_name).builds.export_build(active_build_id, tmp_file)
            self.dest_rack.app(app_name).builds.import_build(active_build_id, tmp_file)
            os.remove(tmp_file)

        return apps

    def _compare(self, apps):
        """ Compare source and destination apps to see if the build id are the same or not """

        self.logger.info('Comparing builds')

        mismatched_build = []

        for app in apps:
            app_name = app['name']

            source_build_id = self.source_rack.app(app_name).builds.active_build_id()

            if not source_build_id:
                continue

            #check if this build already exists on the dest rack
            dest_build = self.dest_rack.app(app_name).builds.get(source_build_id)

            if dest_build and 'error' not in dest_build:
                self.logger.info('Build {} already exists on destination for app {}'.format(source_build_id, app_name))

                continue

            self.logger.info('Build {} not found on destination for app {}'.format(source_build_id, app_name))

            mismatched_build.append(app)

        return mismatched_build
