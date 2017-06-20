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
    parser.add_argument('-v', metavar='Verbosity', type=str, help='Verbosity: INFO|DEBUG', required=False)

    return parser.parse_args()

def main():
    args   = parse_args()
    logger = logging.getLogger('convox-cloner')
    level  = args.v.upper() if not None else 'INFO'

    coloredlogs.install(level=level, logger=logger)

    cloner = ConvoxCloner(source=args.s, destination=args.d, api_key=args.k, logger=logger)
    cloner.clone()

class ConvoxCloner(object):

    def __init__(self, source, destination, api_key, logger):
        self.source      = ConvoxRack(source, api_key, logger)
        self.destination = ConvoxRack(destination, api_key, logger)
        self.logger      = logger

        self.app_sync     = AppSync(self.source, self.destination, self.logger)
        self.env_sync     = EnvironmentSync(self.source, self.destination, self.logger)
        self.build_sync   = BuildSync(self.source, self.destination, self.logger)
        self.release_sync = ReleaseSync(self.source, self.destination, self.logger)

    def clone(self):
        self.logger.info('Cloning {} rack to {} rack'.format(
            self.source.get_rack_name(),
            self.destination.get_rack_name())
        )

        source_app = None
        # source_app= [{'name': 'statflo-webapp-search', 'release': 'RHAQFUOLLEK', 'status': 'running'}]

        self.app_sync.sync(source_app)
        self.env_sync.sync(source_app)
        self.build_sync.sync(source_app)
        self.release_sync.sync(source_app)

if __name__ == '__main__':
    main()
