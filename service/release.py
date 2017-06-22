

class ReleaseSync(object):
    def __init__(self, source_rack, dest_rack, logger):
        self.source_rack = source_rack
        self.dest_rack   = dest_rack
        self.logger      = logger

    def sync(self, source_apps=None):
        source_apps = source_apps if source_apps else self.source_rack.apps.get()

        requiring_update = self._compare(source_apps)

        self._sync(requiring_update)

    def _sync(self, apps):
        """ Promote the release on the destination rack
            that has the same active build from the source rack
        """

        for app in apps:
            app_name = app['name']

            self.logger.info('Promoting build to release for {}.{}'.format(self.dest_rack.name(), app_name))

            source_build_id = self.source_rack.app(app_name).builds.active_build_id()
            release         = self.dest_rack.app(app['name']).releases.get(build_id = source_build_id)

            if not release:
                continue

            release_id = release[0]['id']

            self.dest_rack.app(app_name).releases.promote(release_id)

        return apps

    def _compare(self, apps):
        """ Compare build ids for active releases and if they're not the same then
            promote the release, on the destination, that has this build
        """

        self.logger.info('Comparing builds for release promotion')

        requiring_promotion = []

        for app in apps:
            app_name = app['name']

            source_build_id = self.source_rack.app(app_name).builds.active_build_id()
            dest_build_id   = self.dest_rack.app(app_name).builds.active_build_id()

            if not source_build_id:
                self.logger.info('Build is not present on {}.{}'.format(
                    self.source_rack.name(),
                    app_name)
                )

                continue

            if source_build_id == dest_build_id:
                self.logger.info('Build {} is already active on {}.{}'.format(
                    source_build_id,
                    self.dest_rack.name(),
                    app_name)
                )

                continue
                
            requiring_promotion.append(app)

        return requiring_promotion
