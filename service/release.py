from service.sync import SyncService

class ReleaseSync(SyncService):

    def sync(self, app):
        self.app_name = app['name']

        self._sync(self._compare(app))

    def _sync(self, app):
        """ Promote the release on the destination rack
            that has the same active build from the source rack
        """

        if not app:
            return None

        source_build_id = self.source_rack.app(self.app_name).builds.active_build_id()
        release         = self.dest_rack.app(self.app_name).releases.get(build_id = source_build_id)

        if not release:
            return None

        release_id = release[0]['id']

        self._log('Promoting build {} to release'.format(source_build_id))

        self.dest_rack.app(self.app_name).releases.promote(release_id)

    def _compare(self, app):
        """ Compare build ids for active releases and if they're not the same then
            promote the release, on the destination, that has this build
        """

        if not app:
            return None

        self._log('Comparing build for release promotion')

        source_build_id = self.source_rack.app(self.app_name).builds.active_build_id()
        dest_build_id   = self.dest_rack.app(self.app_name).builds.active_build_id()

        if not source_build_id:
            self._log('No active build')

            return None

        if source_build_id == dest_build_id:
            self._log('Build {} is already active'.format(source_build_id))

            return None

        return app
