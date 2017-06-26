

class ReleaseSync(object):
    def __init__(self, source_rack, dest_rack, logger):
        self.source_rack = source_rack
        self.dest_rack   = dest_rack
        self.logger      = logger

    def sync(self, app=None):
        # source_apps = source_apps if source_apps else self.source_rack.apps.get()

        # requiring_update = self._compare(source_apps)

        self._sync(self._compare(app))

    def _sync(self, app):
        """ Promote the release on the destination rack
            that has the same active build from the source rack
        """

        if not app:
            return None

        app_name = app['name']

        self.logger.info('{}: Promoting build to release'.format(app_name))

        source_build_id = self.source_rack.app(app_name).builds.active_build_id()
        release         = self.dest_rack.app(app['name']).releases.get(build_id = source_build_id)

        if not release:
            return None

        release_id = release[0]['id']

        self.dest_rack.app(app_name).releases.promote(release_id)

    def _compare(self, app):
        """ Compare build ids for active releases and if they're not the same then
            promote the release, on the destination, that has this build
        """

        if not app:
            return None

        app_name = app['name']

        self.logger.info('Comparing build on {} for release promotion'.format(app_name))

        source_build_id = self.source_rack.app(app_name).builds.active_build_id()
        dest_build_id   = self.dest_rack.app(app_name).builds.active_build_id()

        if not source_build_id:
            self.logger.info('{}: Build is not present on {} rack'.format(
                app_name,
                self.source_rack.name(),
                )
            )

            return None

        if source_build_id == dest_build_id:
            self.logger.info('{}: Build {} is already active on {} rack'.format(
                app_name,
                source_build_id,
                self.dest_rack.name(),
                )
            )

            return None

        return app
