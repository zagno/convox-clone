from service.sync import SyncService

class EnvironmentSync(SyncService):

    def sync(self, app, find_replace=None):
        self.app_name = app['name']

        self._sync(self._compare(app), find_replace)

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

    def _sync(self, app, find_replace=None):
        """ Copy all environment variables from the source app to the destination app """

        if not app:
            return

        self._log('Syncing environment variables')

        env_vars = self.source_rack.app(self.app_name).environment.get()
        env_vars = self._find_replace(env_vars, find_replace)
        reponse  = self.dest_rack.app(self.app_name).environment.create(keys=env_vars)


    def _find_replace(self, env_vars, find_replace):
        """ Takes a dict of find and replace values """
        if not find_replace:
            return env_vars

        for find_this, replace_with in find_replace.items():
            for key, value in env_vars.items():
                new_value = value.replace(find_this, replace_with)

                if value == new_value:
                    continue

                self._log('Set env var {} to "{}"'.format(key, new_value))

                env_vars[key] = new_value

        return env_vars
