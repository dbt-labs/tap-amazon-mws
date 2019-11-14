from singer_tap_amazon_mws.streams.base import InventoryIterationStream, pluck, get_price
from singer_tap_amazon_mws.state import incorporate, save_state

from dateutil.parser import parse

import singer
import json
import time
import mws


LOGGER = singer.get_logger()  # noqa


class ProductStream(InventoryIterationStream):
    TABLE = 'products'
    KEY_PROPERTIES = ['id']

    def __init__(self, *args, **kwargs):
        super(ProductStream, self).__init__(*args, **kwargs)

    def get_config(self, product_id):
        return {
            "marketplaceid": self.config.get('marketplace_ids')[0],
            "type_": "SellerSKU",
            "ids": [product_id]
        }

    def parse_product(self, r):
        return {
            # Ids
            'id': pluck(r, ['Id', 'value']),
            'IdType': pluck(r, ['IdType', 'value']),
            'Product': pluck(r, ['Products', 'Product'])
        }

    def get_stream_data(self, result):
        parsed = result.parsed
        LOGGER.info("Parsing data from product")
        parsed_record = self.parse_product(parsed)

        try:
            return self.transform_record(parsed_record)
        except Exception as e:
            if hasattr(parsed, 'Id'):
                LOGGER.info("WARNING: Couldn't sync product with SellerSKU={}; {}".format(parsed.Id, e))
            else:
                LOGGER.info("WARNING: Couldn't sync product {}; {}".format(parsed, e))
            return None

    def sync_records(self, request_config, end_date=None):
        table = self.TABLE
        raw_product =  self.client.fetch_products(request_config)
        product = self.get_stream_data(raw_product)

        if product is not None:
            with singer.metrics.record_counter(endpoint=table) as counter:
                singer.write_records(table, [product])
                counter.increment()

        return product
