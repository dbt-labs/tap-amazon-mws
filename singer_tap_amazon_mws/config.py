
import singer

from dateutil.parser import parse

LOGGER = singer.get_logger()  # noqa


def get_config_start_date(config):
    return parse(config.get('start_date')).date()


def get_config_end_date(config):
    end_date = config.get('end_date')
    if end_date:
        return parse(end_date).date()
    return None
