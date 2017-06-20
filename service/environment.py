

class EnvironmentSync(object):
    def __init__(self, source_rack, dest_rack, logger):
        self.source_rack = source_rack
        self.dest_rack   = dest_rack
        self.logger      = logger

    def sync(self, source_apps=None):
        source_apps = source_apps if source_apps else self.source_rack.apps.get()

        requiring_update = self._compare(source_apps)

        self._sync(requiring_update)

    def _compare(self, source):
        """ Check if the environment variables on the destination are missing,
        incomplete or the values are different from the source variables
        """

        requiring_update = []
        self.logger.info('Checking if env vars for are in-sync')

        for app in source:
            app_name = app['name']

            self.logger.debug('Checking env vars for {}'.format(app_name))

            source_env_vars      = self.source_rack.app(app_name).environment.get()
            destination_env_vars = self.dest_rack.app(app_name).environment.get()

            # Source has vars and destination does not any
            if source_env_vars and not destination_env_vars:
                requiring_update.append(app)

                continue

            # Destination has missing vars
            missing_keys = [
                key
                for key in source_env_vars.keys()
                if key not in destination_env_vars
            ]

            if missing_keys:
                requiring_update.append(app)

                continue

            # If there are no missing vars then check if the values are the different
            mismatched_values = [
                key
                for key in source_env_vars.keys()
                if source_env_vars[key] != destination_env_vars[key]
            ]

            if mismatched_values:
                requiring_update.append(app)

                continue

        if not requiring_update:
            self.logger.info('All app\'s env vars are in sync')
        else:
            self.logger.info('Env var updated needed for some or all apps')

        return requiring_update

    def _sync(self, apps):
        """ Copy all environment variables from the source app to the destination app """

        for app in apps:
            app_name = app['name']

            self.logger.info('Syncing env vars for {}'.format(app_name))

            env_vars = self.source_rack.app(app_name).environment.get()
            reponse  = self.dest_rack.app(app_name).environment.create(keys=env_vars)
