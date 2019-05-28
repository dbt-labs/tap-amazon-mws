import pytz
import singer
import singer.utils
import singer.metrics

from tap_amazon_mws.config import get_config_start_date
from tap_amazon_mws.state import incorporate, save_state, \
    get_last_record_value_for_table

from tap_framework.streams import BaseStream as base

LOGGER = singer.get_logger()


def pluck(r, path):
    for el in path:
        r = r.get(el)
        if r is None:
            return None
    return r


def get_price(record, key):
    if key in record:
        return {
            "CurrencyCode": pluck(record, [key, "CurrencyCode", 'value']),
            "Amount": pluck(record, [key, "Amount", 'value']),
        }
    else:
        return None


class BaseStream(base):
    KEY_PROPERTIES = ['id']

    def sync_data(self):
        pass

class PaginatedStream(BaseStream):

    def sync_data(self):
        table = self.TABLE
        page = 0

        start_date = get_last_record_value_for_table(self.state, table)
        if start_date is None:
            start_date = get_config_start_date(self.config)

        LOGGER.info('Syncing data for entity {} from {} (page={})'.format(table, start_date, page))

        next_token, records = self.sync_records({
            "marketplaceids": self.config.get('marketplace_ids'),
            "lastupdatedafter": start_date,
        })

        while next_token is not None:
            page += 1
            LOGGER.info('Syncing data for entity {} (page={})'.format(table, page))
            next_token, records = self.sync_records({"next_token": next_token})

        return self.state
