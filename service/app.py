

class AppSync(object):
    def __init__(self, source_rack, dest_rack, logger):
        self.source_rack = source_rack
        self.dest_rack   = dest_rack
        self.logger      = logger

    def sync(self, app):
        # source_apps = source_apps if source_apps else self.source_rack.apps.get()


        self._create(
            self._compare(app)
        )

    def _create(self, app):
        """ Creates apps on the destination rack """
        if not app:
            return None

        app_name = app['name']

        self.logger.info('{}: Creating'.format(app_name))

        create = self.dest_rack.apps.create(app_name)

        if 'error' in create:
            self.logger.error("Error: {}" .format(create['error']))

    def _compare(self, app):
        """ Works out which apps are missing on the destination rack """

        if not app:
            return None

        app_name = app['name']

        self.logger.info('{}: Checking if app exists on rack {}'.format(app_name, self.dest_rack.get_rack_name()))

        destination = self.dest_rack.app(app_name).get()

        if 'error' in destination:
            self.logger.info(
                '{}: Missing app on rack {}'.format(app_name, self.dest_rack.get_rack_name())
            )

            return app

        self.logger.info(
            '{}: Found app on rack {}'.format(app_name, self.dest_rack.get_rack_name())
        )

        return None
