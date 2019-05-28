import singer
import singer.metrics

import mws
import time


LOGGER = singer.get_logger()  # noqa


class AmazonMWSClient:

    MAX_TRIES = 5

    def __init__(self, config):
        self.config = config

        self.orders_api = self.get_orders_api()

    def get_orders_api(self):
        return mws.Orders(
            access_key=self.config.get('access_key'),
            secret_key=self.config.get('secret_key'),
            account_id=self.config.get('seller_id'),
            region=self.config.get('region'),
        )

    def fetch_orders(self, request_config):
        exc = None

        for i in range(self.MAX_TRIES):
            try:
                return self.orders_api.list_orders(**request_config)
            except mws.mws.MWSError as e:
                exc = e
                LOGGER.info("Encountered an error while fetching orders, sleeping")
                LOGGER.error(e)
                time.sleep(60 * (i + 1))
        else:
            LOGGER.info("Failed after {} queries - raising".format(self.MAX_TRIES))
            raise exc

    def _fetch_order_items(self, request_config):
        exc = None

        for i in range(self.MAX_TRIES):
            try:
                return self.orders_api.list_order_items(**request_config)
            except mws.mws.MWSError as e:
                exc = e
                LOGGER.info("Encountered an error while fetching order items, sleeping")
                LOGGER.error(e)
                time.sleep(20 * (i + 1))
        else:
            LOGGER.info("Failed after {} queries - raising".format(self.MAX_TRIES))
            raise exc

    def handle_order_items(self, resp):
        if isinstance(resp, dict):
            return [resp]
        else:
            return resp

    def fetch_order_items(self, order_id):
        page = 0
        LOGGER.info("Fetching order items for order={}, page={}".format(order_id, page))

        order_items = []
        resp = self._fetch_order_items({"amazon_order_id": order_id})
        while True:
            new_items = resp.parsed.get('OrderItems', {}).get('OrderItem', [])
            order_items.extend(self.handle_order_items(new_items))

            next_token = resp.parsed.get('NextToken', {}).get('value')
            if next_token:
                page += 1
                LOGGER.info("Fetching order items for order={}, page={}".format(order_id, page))
                resp = self._fetch_order_items({"next_token": next_token})
            else:
                break

        return order_items
