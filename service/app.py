from service.sync import SyncService

class AppSync(SyncService):

    def sync(self, app):
        self.app_name = app['name']

        self._create(
            self._compare(app)
        )

    def _create(self, app):
        """ Creates apps on the destination rack """
        if not app:
            return None

        self._log('Creating')

        create = self.dest_rack.apps.create(self.app_name)

        if 'error' in create:
            self.logger.error("Error: {}" .format(create['error']))

    def _compare(self, app):
        """ Works out which apps are missing on the destination rack """

        if not app:
            return None

        self._log('Checking if app exists')

        destination = self.dest_rack.app(self.app_name).get()

        if 'error' in destination:
            self._log('Missing app')

            return app

        self._log('Found app')

        return None
