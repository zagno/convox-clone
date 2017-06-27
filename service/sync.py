class SyncService(object):

    def __init__(self, source_rack, dest_rack, logger):
        self.source_rack    = source_rack
        self.dest_rack      = dest_rack
        self.logger         = logger
        self.app_name       = None
        self.dest_rack_name = self.dest_rack.get_rack_name()

    def _log(self, message, rack_name = None):
        rack_name = rack_name if not None else self.dest_rack_name

        self.logger.info('{}: {} on rack {}'.format(
            self.app_name,
            message,
            self.dest_rack_name
        ))
