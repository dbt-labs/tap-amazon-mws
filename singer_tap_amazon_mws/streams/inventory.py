from singer_tap_amazon_mws.streams.base import PaginatedStream, pluck, get_price
from singer_tap_amazon_mws.state import incorporate, save_state
from singer_tap_amazon_mws.cache import InventoryCache

from dateutil.parser import parse

import singer
import json
import time
import mws


LOGGER = singer.get_logger()  # noqa

DEFAULT_INVENTORY_START_DATE = "2001-01-01"


class InventoryStream(PaginatedStream):
    TABLE = 'inventory'
    KEY_PROPERTIES = ['id']

    def __init__(self, *args, **kwargs):
        super(InventoryStream, self).__init__(*args, **kwargs)

    def get_config(self, _):
        start_date = self.config.get("inventory_start_date", DEFAULT_INVENTORY_START_DATE)
        start_date_dt = parse(start_date).date()

        return {
            "datetime": start_date_dt,
            "response_group": "Basic"
        }

    def parse_inventory_item(self, r):
        return {
            # Ids
            "id": pluck(r, ['SellerSKU', 'value']),
            "ASIN": pluck(r, ['ASIN', 'value']),
            "FNSKU": pluck(r, ['FNSKU', 'value']),
            "SellerSKU": pluck(r, ['SellerSKU', 'value']),

            "Condition": pluck(r, ['Condition', 'value']),
            "SupplyDetail": pluck(r, ['SupplyDetail', 'value']),
            "TotalSupplyQuantity": pluck(r, ['TotalSupplyQuantity', 'value']),
            "InStockSupplyQuantity": pluck(r, ['InStockSupplyQuantity', 'value']),
            "EarliestAvailability": pluck(r, ['EarliestAvailability', 'TimepointType', 'value']),
        }

    def get_stream_data(self, result):
        parsed = result.parsed
        inventory_supply_list = parsed.get('InventorySupplyList', {})
        inventory_list = inventory_supply_list.get('member', [])

        # Shove this into a list if its a dict
        # This can happen when only one record is returned by the API
        #   because the XML response does not encode list/dict info
        if isinstance(inventory_list, dict):
            inventory_list = [inventory_list]

        LOGGER.info("Parsing data from {} inventory records".format(len(inventory_list)))

        records = []
        for record in inventory_list:
            parsed_record = self.parse_inventory_item(record)
            records.append(self.transform_record(parsed_record))

        return records

    def sync_records(self, request_config, end_date=None):
        table = self.TABLE
        raw_inventory =  self.client.fetch_inventory(request_config)
        inventory = self.get_stream_data(raw_inventory)

        with singer.metrics.record_counter(endpoint=table) as counter:
            singer.write_records(table, inventory)
            counter.increment(len(inventory))

        for record in inventory:
            InventoryCache[record['id']] = record

        next_token = raw_inventory.parsed.get('NextToken', {}).get('value')
        return next_token, inventory
