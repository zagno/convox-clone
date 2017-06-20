

class AppSync(object):
    def __init__(self, source_rack, dest_rack, logger):
        self.source_rack = source_rack
        self.dest_rack   = dest_rack
        self.logger      = logger

    def sync(self, source_apps=None, dest_apps=None):
        source_apps = source_apps if source_apps else self.source_rack.apps.get()
        dest_apps   = dest_apps if dest_apps else self.dest_rack.apps.get()

        self._create(
            self._compare(source_apps, dest_apps)
        )

    def _create(self, apps):
        """ Creates apps on the destination rack """
        for app in apps:
            self.logger.info('Creating Application {}'.format(app['name']))

            create = self.dest_rack.apps.create(app['name'])

            if 'error' in create:
                self.logger.error("Error: {}" .format(create['error']))

    def _compare(self, source, destination):
        """ Works out which apps are missing on the destination rack """

        self.logger.info('Checking for missing applications on the destination')

        missing_apps = [
            source_app
            for source_app in source
            if source_app['name'] not in
            [destination_app['name'] for destination_app in destination]
        ]

        if not missing_apps:
            self.logger.info(
                'No applications missing on the {} rack'.format(self.dest_rack.get_rack_name())
            )
        else:
            self.logger.info(
                'Missing applications found on the {} rack'.format(self.dest_rack.get_rack_name())
            )

        return missing_apps
