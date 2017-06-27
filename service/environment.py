from service.sync import SyncService

class EnvironmentSync(SyncService):

    def sync(self, app):
        self.app_name = app['name']

        self._sync(self._compare(app))

    def _compare(self, app):
        """ Check if the environment variables on the destination are missing,
        incomplete or the values are different from the source variables
        """
        if not app:
            return

        requiring_update = []

        self._log('Comparing environment variables')

        source_env_vars      = self.source_rack.app(self.app_name).environment.get()
        destination_env_vars = self.dest_rack.app(self.app_name).environment.get()

        # Source has vars and destination does not any
        if source_env_vars and not destination_env_vars:
            return app

        # Destination has missing vars
        missing_keys = [
            key
            for key in source_env_vars.keys()
            if key not in destination_env_vars
        ]

        if missing_keys:
            return app

        # If there are no missing vars then check if the values are the different
        mismatched_values = [
            key
            for key in source_env_vars.keys()
            if source_env_vars[key] != destination_env_vars[key]
        ]

        if mismatched_values:
            return app

        self._log('Environment variables are in-sync')

        return None

    def _sync(self, app):
        """ Copy all environment variables from the source app to the destination app """

        if not app:
            return

        self._log('Syncing environment variables')

        env_vars = self.source_rack.app(self.app_name).environment.get()
        reponse  = self.dest_rack.app(self.app_name).environment.create(keys=env_vars)
