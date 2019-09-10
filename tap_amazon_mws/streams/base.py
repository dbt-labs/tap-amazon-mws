import singer
import singer.utils
import singer.metrics

from tap_amazon_mws.cache import InventoryCache
from tap_amazon_mws.config import get_config_start_date, get_config_end_date
from tap_amazon_mws.state import get_last_record_value_for_table

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

        end_date = get_config_end_date(self.config)

        LOGGER.info('Syncing data for entity {} from {} (page={})'.format(table, start_date, page))

        next_token, records = self.sync_records(self.get_config(start_date), end_date=end_date)

        while next_token is not None:
            page += 1
            LOGGER.info('Syncing data for entity {} (page={})'.format(table, page))
            next_token, records = self.sync_records({"next_token": next_token}, end_date=end_date)

        return self.state


class InventoryIterationStream(BaseStream):

    def sync_data(self):
        table = self.TABLE

        LOGGER.info('Syncing data for {} {}'.format(len(InventoryCache), table))

        for i, product_id in enumerate(sorted(InventoryCache)):
            LOGGER.info('Syncing data for product {} of {} {}'.format(i + 1, len(InventoryCache), product_id))
            self.sync_records(self.get_config(product_id=product_id))

        return self.state
