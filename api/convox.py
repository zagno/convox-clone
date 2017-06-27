import requests
from requests.auth import HTTPBasicAuth
from threading import Thread
from pprint import pprint

class ConvoxBaseAPI(object):
    def __init__(self, rack, api_key, logger):
        self.api_url = 'https://console.convox.com'
        self.rack     = rack
        self.api_key  = api_key
        self.logger   = logger

    def _get(self, uri):
        try:
            url = '{}{}'.format(self.api_url, uri)

            self.logger.debug('GET {}'.format(url))

            return requests.get(
                url,
                auth=(self.rack , self.api_key),
                headers={'rack': self.rack}
            ).json()
        except Exception as e:
            return None

    def _post(self, uri, payload = None):
        try:
            url = '{}{}'.format(self.api_url, uri)

            self.logger.debug('POST {}'.format(url))

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

class ConvoxRack(ConvoxBaseAPI):
    def __init__(self, rack, api_key, logger):
        super().__init__(rack, api_key, logger)

        self.apps = ConvoxApps(rack, api_key, logger)
        self.app_cache = []

    def app(self, app_name, apps_cache = {}):
        return ConvoxApp(self.rack, self.api_key, app_name, self.logger)

    def apps(self):
        return self.apps

    def name(self):
        return self.rack

class ConvoxApp(ConvoxBaseAPI):
    def __init__(self, rack, api_key, app_name, logger):
        super().__init__(rack, api_key, logger)

        self.app_name    = app_name
        self.environment = ConvoxEnvironment(rack, api_key, logger, app=self)
        self.builds      = ConvoxBuilds(rack, api_key, logger, app=self)
        self.releases    = ConvoxReleases(rack, api_key, logger, app=self)

    def get(self):
        return self._get('/apps/{}'.format(self.app_name))

    def name(self):
        return self.app_name

class ConvoxApps(ConvoxBaseAPI):
    def __init__(self,rack, api_key, logger):
        super().__init__(rack, api_key, logger)

    def get(self):
        return super()._get('/apps')

    def create(self, app_name):
        return super()._post('/apps', {'name': app_name})

class ConvoxEnvironment(ConvoxBaseAPI):
    def __init__(self, rack, api_key, logger, app):
        super().__init__(rack, api_key, logger)

        self.app = app

    def get(self, key = None):
        if key:
            return self._get('/apps/{}/environment/{}'.format(self.app.name(), key))

        return self._get('/apps/{}/environment'.format(self.app.name()))

    def create(self, keys=None, key=None):
        if keys:
            config = ''
            for key, value in keys.items():
                config += "{}={}\n".format(key, value)

            return self._post(
                uri = '/apps/{}/environment'.format(self.app.name()),
                payload=config
            )

        if key:
            pass

class ConvoxBuilds(ConvoxBaseAPI):
    def __init__(self, rack, api_key, logger, app):
        super().__init__(rack, api_key, logger)

        self.logger   = logger
        self.app      = app

    def active_build_id(self):
        self.logger.debug('Working out active build for {}.{}'.format(
            self.app.name(),
            self.app.get_rack_name()
        ))

        app_info = self.app.get()

        if not app_info:
            return None

        release_info = self.app.releases.get(app_info['release'])

        if not release_info:
            return None

        if not 'build' in release_info:
            return None

        return release_info['build']

    def get(self, build_id=None):
        if build_id:
            return self._get('/apps/{}/builds/{}'.format(self.app.name(), build_id))

        return self._get('/apps/{}/builds'.format(self.app.name()))

    def export_build(self, build_id, file_name):
        self.logger.debug('Retrieving build {} and saving to {}'.format(build_id, file_name))

        url = '{}/apps/{}/builds/{}.tgz'.format(self.api_url, self.app.name(), build_id)



        with open(file_name, 'wb') as f:
            r = requests.get(
                url,
                auth=(self.rack , self.api_key),
                headers={'rack': self.rack},
                stream=True
            )

            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

            r.close()
        return

    def import_build(self, build_id, file_name):
        self.logger.debug('Sending file {} and creating build {}'.format(file_name, build_id))

        files = {'image': (build_id, open(file_name, 'rb'))}

        r = requests.post(
            '{}/apps/{}/builds'.format(self.api_url, self.app.name()),
            files=files,
            auth=(self.rack , self.api_key),
            headers={'rack': self.rack},
            stream=True
        )


class ConvoxReleases(ConvoxBaseAPI):
    def __init__(self, rack, api_key, logger, app):
        super().__init__(rack, api_key, logger)

        self.logger   = logger
        self.app      = app

    def get(self, release_id=None, build_id=None):
        if not release_id:
            data = self._get('/apps/{}/releases'.format(self.app.name()))
        else:
            data = self._get('/apps/{}/releases/{}'.format(self.app.name(), release_id))

        if not build_id:
            return data

        return [
            item
            for item in data
            if 'build' in item and item['build'] == build_id
        ]

    def promote(self, release_id):
        self.logger.debug('Promoting release {} for app {} on rack {}'.format(release_id, self.app.name(), self.rack))

        return self._post('/apps/{}/releases/{}/promote'.format(self.app.name(), release_id))


    def latest(self):
        releases = self.get()

        if not releases:
            return None

        return releases[0]

    def latest_release_id(self):
        release = self.latest()

        if not release:
            return None

        return release['id']
