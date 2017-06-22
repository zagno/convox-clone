#! /usr/bin/env python3

import sys
import argparse

from pprint import pprint
import coloredlogs, logging

from api.convox import *
from service.app import AppSync
from service.environment import EnvironmentSync
from service.build import BuildSync
from service.release import ReleaseSync

def parse_args():
    parser = argparse.ArgumentParser(description='Clones apps from one rack ')

    parser.add_argument('-s', metavar='Ssurce', type=str, help='source rack', required=True)
    parser.add_argument('-d', metavar='destination', type=str, help='destination rack', required=True)
    parser.add_argument('-k', metavar='key', type=str, help='API key', required=True)
    parser.add_argument('-v', metavar='Verbosity', type=str, help='Verbosity: INFO|DEBUG', default='INFO', required=False)
    parser.add_argument('-a', metavar='application', type=str, help='Application name', nargs='*', required=False)

    return parser.parse_args()

def main():
    args   = parse_args()
    logger = logging.getLogger('convox-cloner')
    level  = args.v.upper() if not None else 'INFO'

    coloredlogs.install(level=level, logger=logger)

    cloner = ConvoxCloner(source=args.s, destination=args.d, api_key=args.k, logger=logger)

    cloner.clone(args.a)

class ConvoxCloner(object):

    def __init__(self, source, destination, api_key, logger):
        self.source      = ConvoxRack(source, api_key, logger)
        self.destination = ConvoxRack(destination, api_key, logger)
        self.logger      = logger

        self.app_sync     = AppSync(self.source, self.destination, self.logger)
        self.env_sync     = EnvironmentSync(self.source, self.destination, self.logger)
        self.build_sync   = BuildSync(self.source, self.destination, self.logger)
        self.release_sync = ReleaseSync(self.source, self.destination, self.logger)

    def clone(self, app_names = None):
        source_apps = []
        dest_apps   = []
        source_name = self.source.get_rack_name()
        dest_name   = self.destination.get_rack_name()

        message = 'Cloning All apps from {} rack to {} rack'.format(source_name, dest_name)

        for app_name in app_names:
            source_apps.append(self.source.app(app_name).get())

        if source_apps:
            message = "Cloning apps: {} from {} rack to {} rack".format(
                ', '.join([item['name'] for item in source_apps]),
                source_name,
                dest_name
            )

        self.logger.info(message)

        self.app_sync.sync(source_apps)
        self.env_sync.sync(source_apps)
        self.build_sync.sync(source_apps)
        self.release_sync.sync(source_apps)

if __name__ == '__main__':
    main()
