

class EnvironmentSync(object):
    def __init__(self, source_rack, dest_rack, logger):
        self.source_rack = source_rack
        self.dest_rack   = dest_rack
        self.logger      = logger

    def sync(self, source_apps=None):
        source_apps = source_apps if source_apps else self.source_rack.apps.get()

        self._sync(self._compare(source_apps))

    def _compare(self, app):
        """ Check if the environment variables on the destination are missing,
        incomplete or the values are different from the source variables
        """
        if not app:
            return

        app_name = app['name']
        requiring_update = []
        self.logger.info('{}: Comparing environment variables'.format(app_name))


        self.logger.debug('{}: Checking environment variables'.format(app_name))

        source_env_vars      = self.source_rack.app(app_name).environment.get()
        destination_env_vars = self.dest_rack.app(app_name).environment.get()

        # Source has vars and destination does not any
        if source_env_vars and not destination_env_vars:
            requiring_update.append(app)

            return None

        # Destination has missing vars
        missing_keys = [
            key
            for key in source_env_vars.keys()
            if key not in destination_env_vars
        ]

        if missing_keys:
            requiring_update.append(app)

            return None

        # If there are no missing vars then check if the values are the different
        mismatched_values = [
            key
            for key in source_env_vars.keys()
            if source_env_vars[key] != destination_env_vars[key]
        ]

        if mismatched_values:
            requiring_update.append(app)

            return None

        self.logger.info('{}: Environment variables are in-sync'.format(app_name))

        return requiring_update

    def _sync(self, app):
        """ Copy all environment variables from the source app to the destination app """

        if not app:
            return

        app_name = app['name']

        self.logger.info('{}: Syncing environment variables'.format(app_name))

        env_vars = self.source_rack.app(app_name).environment.get()
        reponse  = self.dest_rack.app(app_name).environment.create(keys=env_vars)
