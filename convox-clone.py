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
from multiprocessing import Pool

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

    apps      =[]
    arguments = []
    source    = ConvoxRack(args.s, args.k, logger)

    if args.a:
        for app in args.a:
            apps.append(source.app(app).get())
    else:
        apps = source.apps.get()

    if apps:
        logger.info("Cloning apps: {} from {} rack to {} rack".format(
            ', '.join([item['name'] for item in apps]),
            args.s,
            args.d
        ))

    for app in apps:
        arguments.append({
            'source' : args.s,
            'destination': args.d,
            'api_key': args.k,
            'app':app
        })

    with Pool(processes=5,maxtasksperchild=100) as p:
        p.map(run, arguments)

def run(arguments):
    logger = logging.getLogger('convox-cloner')
    # level  = args.v.upper() if not None else 'INFO'
    level ='DEBUG'

    coloredlogs.install(level=level, logger=logger)

    cloner = ConvoxCloner(**arguments, logger=logger)
    cloner.clone()

class ConvoxCloner(object):

    def __init__(self, source, destination, api_key, logger, app=None):
        self.source      = ConvoxRack(source, api_key, logger)
        self.destination = ConvoxRack(destination, api_key, logger)
        self.logger      = logger
        self.app         = app

        self.app_sync     = AppSync(self.source, self.destination, self.logger)
        self.env_sync     = EnvironmentSync(self.source, self.destination, self.logger)
        self.build_sync   = BuildSync(self.source, self.destination, self.logger)
        self.release_sync = ReleaseSync(self.source, self.destination, self.logger)

    def clone(self):
        source_name = self.source.get_rack_name()
        dest_name   = self.destination.get_rack_name()

        self.app_sync.sync(self.app)
        self.env_sync.sync(self.app)
        self.build_sync.sync(self.app)
        self.release_sync.sync(self.app)

if __name__ == '__main__':
    main()
