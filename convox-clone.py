#! /usr/bin/env python3

import sys
import argparse
import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint
import coloredlogs, logging

def parse_args():
    parser = argparse.ArgumentParser(description='Clones apps from one rack ')

    parser.add_argument('-s', metavar='Ssurce', type=str, help='source rack', required=True)
    parser.add_argument('-d', metavar='destination', type=str, help='destination rack', required=True)
    parser.add_argument('-k', metavar='key', type=str, help='API key', required=True)

    return parser.parse_args()

def main():
    args   = parse_args()
    logger = logging.getLogger('convox-cloner')
    coloredlogs.install(level='INFO', logger=logger)

    cloner = ConvoxCloner(source=args.s, destination=args.d, api_key=args.k, logger=logger)
    cloner.clone()

class ConvoxCloner():

    def __init__(self, source, destination, api_key, logger):
        self.source      = ConvoxApi(source, api_key, logger)
        self.destination = ConvoxApi(destination, api_key, logger)
        self.logger      = logger

    def clone(self):
        self.logger.info('Cloning {} rack to {} rack'.format(
            self.source.get_rack_name(),
            self.destination.get_rack_name())
        )

        source_apps = self._get_app_nams_as_list(self.source)
        destination_apps = self._get_app_nams_as_list(self.destination)

        self._create_apps(
            self._get_missing_apps(source_apps, destination_apps)
        )

        self._sync_enviroment_variables_for_apps(
            self._get_apps_needing_updates(source_apps)
        )

    def _create_apps(self, apps):
        for app in apps:
            self.logger.info('Creating Application {}'.format(app))

            create = self.destination.apps.create(app)

            if 'error' in create:
                self.logger.error("Error: {}" .format(create['error']))

    def _sync_enviroment_variables_for_apps(self, apps):
        for app in apps:
            self.logger.info('Syncing env vars for {}'.format(app))

            env_vars = self.source.app(app).environment.get()
            respone  = self.destination.app(app).environment.create(keys=env_vars)

    def _get_app_nams_as_list(self, rack):
        apps = []

        for app in rack.apps.get():
            apps.append(app['name'])

        return apps

    def _get_apps_needing_updates(self, source):
        requiring_update = []
        self.logger.info('Checking if env vars for are in-sync')

        for app in source:
            self.logger.debug('Checking env vars for {}'.format(app))

            source_env_vars      = self.source.app(app).environment.get()
            destination_env_vars = self.destination.app(app).environment.get()

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
            self.logger.info('All env vars are in sync')
        else:
            self.logger.info('env var updated needed for: {}'.format(requiring_update))

        return requiring_update

    def _get_missing_apps(self, source, destination):
        self.logger.info('Checking for missing applications')

        missing_apps = [app for app in source if app not in destination]

        if not missing_apps:
            self.logger.info(
                'No applications missing on the {} rack'.format(self.destination.get_rack_name())
            )
        else:
            self.logger.info(
                'Missing applications found on the {} rack: {}'.format(self.destination.get_rack_name(), missing_apps)
            )

        return [app for app in source if app not in destination]

class ConvoxApi:
    def __init__(self, rack, api_key,logger):
        self.api_base = 'https://console.convox.com'
        self.rack     = rack
        self.api_key  = api_key
        self.logger   = logger
        self.apps     = ConvoxApps(rack, api_key, logger)

    def _get(self, api_path):
        try:
            return requests.get(
                '{}{}'.format(self.api_base, api_path),
                auth=(self.rack , self.api_key),
                headers={'rack': self.rack}
            ).json()
        except Exception as e:
            return None

    def _post(self, api_path, payload):
        try:
            url = '{}{}'.format(self.api_base, api_path)
            return requests.post(
                url,
                auth=(self.rack , self.api_key),
                data=payload,
                headers={'rack': self.rack}
            ).json()
        except Exception:
            return None

    def get_rack_name(self):
        return self.rack

    def app(self, app_name):
        return ConvoxApp(self.rack, self.api_key, app_name, self.logger)

    def apps(self):
        return self.apps

class ConvoxApp(ConvoxApi):
    def __init__(self, rack, api_key, app_name, logger):
        self.api_base    = 'https://console.convox.com'
        self.rack        = rack
        self.api_key     = api_key
        self.app_name    = app_name
        self.logger      = logger
        self.environment = ConvoxEnvironment(rack, api_key, app_name, logger)

class ConvoxApps(ConvoxApi):
    def __init__(self, rack, api_key, logger):
        self.api_base    = 'https://console.convox.com'
        self.rack        = rack
        self.api_key     = api_key
        self.logger      = logger

    def get(self):
        return super()._get('/apps')

    def create(self, app_name):
        return super()._post('/apps', {'name': app_name})

class ConvoxEnvironment(ConvoxApi):
    def __init__(self, rack, api_key, app_name, logger):
        self.api_base = 'https://console.convox.com'
        self.rack     = rack
        self.api_key  = api_key
        self.app_name = app_name
        self.logger   = logger

    def get(self, key = None):
        if key:
            return self._get('/apps/{}/environment/{}'.format(self.app_name, key))

        return self._get('/apps/{}/environment'.format(self.app_name))

    def create(self, keys=None, key=None):
        if keys:
            config = ''
            for key, value in keys.items():
                config += "{}={}\n".format(key, value)

            return self._post(
                api_path = '/apps/{}/environment'.format(self.app_name),
                payload=config
            )

        if key:
            pass

            # return self._get('/apps/{}/environment'.format(self.app_name))

if __name__ == '__main__':
    main()
