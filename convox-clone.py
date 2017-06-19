#! /usr/bin/env python3

import sys
import argparse
import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint

def parse_args():
    parser = argparse.ArgumentParser(description='Clones apps from one rack to another rack')

    parser.add_argument('-s', metavar='FILE', type=str, nargs='+', help='source rack')
    parser.add_argument('-d', metavar='FILE', type=str, nargs='+', help='destination rack')
    parser.add_argument('-a', metavar='FILE', type=str, nargs='+', help='API key')

    return parser.parse_args()

def main():
    args = parse_args()

    cloner = ConvoxCloner(args.s[0], args.d[0], args.a[0])

    cloner.clone()

class ConvoxCloner():

    def __init__(self, source, destination, api_key):
        self.source      = Convox(source, api_key)
        self.destination = Convox(destination, api_key)

    def clone(self):
        apps = self._get_source_apps()

        self._create_apps(apps);
        self._sync_enviroment_variables(apps)

    def _create_apps(self, apps):
        for app in apps:
            print('Creating Application {}'.format(app))

            create = self.destination.apps.create(app)

            if 'error' in create:
                print("Error: {}" .format(create['error']))

    def _sync_enviroment_variables(self, apps):
        for app in apps:
            print('Syncing ENV vars for {}'.format(app))

            env_vars = self.source.app(app).environment.get()

            respone = self.destination.app(app).environment.create(keys=env_vars)

    def _get_source_apps(self):
        apps = []

        for app in self.source.apps.get():
            apps.append(app['name'])

        return apps

class Convox:
    def __init__(self, rack, api_key):
        self.api_base = 'https://console.convox.com'
        self.rack     = rack
        self.api_key  = api_key
        self.apps     = ConvoxApps(rack, api_key)

    def _get(self, api_path):
        try:
            return requests.get(
                '{}{}'.format(self.api_base, api_path),
                auth=(self.rack , self.api_key),
                headers={'rack': self.rack}
            ).json()
        except Exception as e:
            pprint(e)
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

    def app(self, app_name):
        return ConvoxApp(self.rack, self.api_key, app_name)

    def apps(self):
        return self.apps

class ConvoxApp(Convox):
    def __init__(self, rack, api_key, app_name):
        self.api_base    = 'https://console.convox.com'
        self.rack        = rack
        self.api_key     = api_key
        self.app_name    = app_name
        self.environment = ConvoxEnvironment(rack, api_key, app_name)

class ConvoxApps(Convox):
    def __init__(self, rack, api_key):
        self.api_base    = 'https://console.convox.com'
        self.rack        = rack
        self.api_key     = api_key

    def get(self):
        return super()._get('/apps')

    def create(self, app_name):
        return super()._post('/apps', {'name': app_name})

class ConvoxEnvironment(Convox):
    def __init__(self, rack, api_key, app_name):
        self.api_base = 'https://console.convox.com'
        self.rack     = rack
        self.api_key  = api_key
        self.app_name = app_name

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
