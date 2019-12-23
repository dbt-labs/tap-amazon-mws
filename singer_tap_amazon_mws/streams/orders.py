from singer_tap_amazon_mws.streams.base import PaginatedStream, pluck, get_price
from singer_tap_amazon_mws.state import incorporate, save_state
from dateutil.parser import parse

import singer
import time


LOGGER = singer.get_logger()  # noqa


class OrdersStream(PaginatedStream):
    TABLE = 'orders'
    KEY_PROPERTIES = ['id']

    def __init__(self, *args, **kwargs):
        super(OrdersStream, self).__init__(*args, **kwargs)

    def get_config(self, start_date):
        return {
            "marketplaceids": self.config.get('marketplace_ids'),
            "lastupdatedafter": start_date,
            "max_results": "50"
        }

    def parse_order_item(self, r):
        return {
            # Ids
            "id": pluck(r, ['AmazonOrderId', 'value']),
            "SellerOrderId": pluck(r, ['SellerOrderId', 'value']),
            "AmazonOrderId": pluck(r, ['AmazonOrderId', 'value']),
            "MarketplaceId": pluck(r, ['MarketplaceId', 'value']),

            # Strings
            "OrderStatus": pluck(r, ['OrderStatus', 'value']),
            "OrderType": pluck(r, ['OrderType', 'value']),
            "BuyerName": pluck(r, ['BuyerName', 'value']),
            "BuyerEmail": pluck(r, ['BuyerEmail', 'value']),
            "ShipServiceLevel": pluck(r, ['ShipServiceLevel', 'value']),
            "ShipServiceLevelCategory": pluck(r, ['ShipServiceLevelCategory', 'value']),
            "SalesChannel": pluck(r, ['SalesChannel', 'value']),
            "FulfillmentChannel": pluck(r, ['FulfillmentChannel', 'value']),
            "PaymentMethod": pluck(r, ['PaymentMethod', 'value']),

            # Dates
            "PurchaseDate": pluck(r, ['PurchaseDate', 'value']),
            "EarliestShipDate": pluck(r, ['EarliestShipDate', 'value']),
            "LatestShipDate": pluck(r, ['LatestShipDate', 'value']),
            "LastUpdateDate": pluck(r, ['LastUpdateDate', 'value']),

            # Counts
            "NumberOfItemsShipped": pluck(r, ['NumberOfItemsShipped', 'value']),
            "NumberOfItemsUnshipped": pluck(r, ['NumberOfItemsUnshipped', 'value']),

            # bools
            "IsReplacementOrder": pluck(r, ['IsReplacementOrder', 'value']),
            "IsBusinessOrder": pluck(r, ['IsBusinessOrder', 'value']),
            "IsPrime": pluck(r, ['IsPrime', 'value']),
            "IsPremiumOrder": pluck(r, ['IsPremiumOrder', 'value']),

            # Structs
            "ShippingAddress": {
                "City": pluck(r, ['ShippingAddress', 'City', 'value']),
                "PostalCode": pluck(r, ['ShippingAddress', 'PostalCode', 'value']),
                "StateOrRegion": pluck(r, ['ShippingAddress', 'StateOrRegion', 'value']),
                "CountryCode": pluck(r, ['ShippingAddress', 'CountryCode', 'value']),
                "Name": pluck(r, ['ShippingAddress', 'Name', 'value']),
                "AddressLine1": pluck(r, ['ShippingAddress', 'AddressLine1', 'value']),
                "AddressLine2": pluck(r, ['ShippingAddress', 'AddressLine2', 'value'])
            },

            # Prices
            "OrderTotal": get_price(r, 'OrderTotal'),
            "ShippingDiscount": get_price(r, 'ShippingDiscount'),
            "PromotionDiscount": get_price(r, 'PromotionDiscount')
        }

    def parse_order(self, r):
        return {
            # Ids
            "id": pluck(r, ['AmazonOrderId', 'value']),
            "SellerOrderId": pluck(r, ['SellerOrderId', 'value']),
            "AmazonOrderId": pluck(r, ['AmazonOrderId', 'value']),
            "MarketplaceId": pluck(r, ['MarketplaceId', 'value']),

            # Strings
            "OrderStatus": pluck(r, ['OrderStatus', 'value']),
            "OrderType": pluck(r, ['OrderType', 'value']),
            "BuyerName": pluck(r, ['BuyerName', 'value']),
            "BuyerEmail": pluck(r, ['BuyerEmail', 'value']),
            "ShipServiceLevel": pluck(r, ['ShipServiceLevel', 'value']),
            "ShipServiceLevelCategory": pluck(r, ['ShipServiceLevelCategory', 'value']),
            "SalesChannel": pluck(r, ['SalesChannel', 'value']),
            "FulfillmentChannel": pluck(r, ['FulfillmentChannel', 'value']),
            "PaymentMethod": pluck(r, ['PaymentMethod', 'value']),

            # Dates
            "PurchaseDate": pluck(r, ['PurchaseDate', 'value']),
            "EarliestShipDate": pluck(r, ['EarliestShipDate', 'value']),
            "LatestShipDate": pluck(r, ['LatestShipDate', 'value']),
            "LastUpdateDate": pluck(r, ['LastUpdateDate', 'value']),

            # Counts
            "NumberOfItemsShipped": pluck(r, ['NumberOfItemsShipped', 'value']),
            "NumberOfItemsUnshipped": pluck(r, ['NumberOfItemsUnshipped', 'value']),

            # bools
            "IsReplacementOrder": pluck(r, ['IsReplacementOrder', 'value']),
            "IsBusinessOrder": pluck(r, ['IsBusinessOrder', 'value']),
            "IsPrime": pluck(r, ['IsPrime', 'value']),
            "IsPremiumOrder": pluck(r, ['IsPremiumOrder', 'value']),

            # Structs
            "ShippingAddress": {
                "City": pluck(r, ['ShippingAddress', 'City', 'value']),
                "PostalCode": pluck(r, ['ShippingAddress', 'PostalCode', 'value']),
                "StateOrRegion": pluck(r, ['ShippingAddress', 'StateOrRegion', 'value']),
                "CountryCode": pluck(r, ['ShippingAddress', 'CountryCode', 'value']),
                "Name": pluck(r, ['ShippingAddress', 'Name', 'value']),
                "AddressLine1": pluck(r, ['ShippingAddress', 'AddressLine1', 'value']),
                "AddressLine2": pluck(r, ['ShippingAddress', 'AddressLine2', 'value'])
            },

            # Prices
            "OrderTotal": get_price(r, 'OrderTotal'),
            "ShippingDiscount": get_price(r, 'ShippingDiscount'),
            "PromotionDiscount": get_price(r, 'PromotionDiscount'),
        }

    def sync_order_items(self, order_id):
        order_items = self.client.fetch_order_items(order_id)
        time.sleep(1)

        parsed = []
        for o in order_items:
            parsed.append({
                "QuantityOrdered": pluck(o, ['QuantityOrdered', 'value']),
                "QuantityShipped": pluck(o, ['QuantityShipped', 'value']),
                "Title": pluck(o, ['Title', 'value']),
                "IsGift": pluck(o, ['IsGift', 'value']),
                "ASIN": pluck(o, ['ASIN', 'value']),
                "SellerSKU": pluck(o, ['SellerSKU', 'value']),
                "OrderItemId": pluck(o, ['OrderItemId', 'value']),
                "IsTransparency": pluck(o, ['IsTransparency', 'value']),
                "CustomizedURL": pluck(o, ['BuyerCustomizedInfo', 'CustomizedURL', 'value']),
                "ProductInfo": {
                    "NumberOfItems": pluck(o, ['ProductInfo', 'NumberOfItems', 'value']),
                    "SerialNumberRequired": pluck(o, ['ProductInfo', 'SerialNumberRequired', 'value']),
                },
                "ItemPrice": get_price(o, 'ItemPrice'),
                "ItemTax": get_price(o, 'ItemTax'),
                "PromotionDiscount": get_price(o, 'PromotionDiscount'),
                "PromotionDiscountTax": get_price(o, 'PromotionDiscountTax'),
            })

        return parsed

    def get_stream_data(self, result):
        parsed = result.parsed
        for path in ['Orders', 'Order']:
            if path not in parsed:
                parsed = []
                break
            else:
                parsed = parsed.get(path)

        # Shove this into a list if its a dict
        # This can happen when only one record is returned by the API
        #   because the XML response does not encode list/dict info
        if isinstance(parsed, dict):
            parsed = [parsed]

        if len(parsed) > 0:
            LOGGER.info("Extracting data from {} orders ({} - {})".format(
                len(parsed), parsed[0]['LastUpdateDate'], parsed[-1]['LastUpdateDate']
            ))
        else:
            LOGGER.info("No orders returned!")

        records = []
        for record in parsed:
            parsed_record = self.parse_order(record)
            parsed_record["OrderItems"] = self.sync_order_items(parsed_record['AmazonOrderId'])
            records.append(self.transform_record(parsed_record))

        if len(records) > 0:
            LOGGER.info('DEBUG: last record is from: {}'.format(records[-1]['LastUpdateDate']))
        return records

    def sync_records(self, request_config, end_date=None):
        table = self.TABLE
        raw_orders =  self.client.fetch_orders(request_config)
        orders = self.get_stream_data(raw_orders)

        with singer.metrics.record_counter(endpoint=table) as counter:
            singer.write_records(table, orders)
            counter.increment(len(orders))

        if len(orders) > 0:
            state_key = 'LastUpdateDate'
            last_order = orders[-1]
            order_time = last_order[state_key]
            self.state = incorporate(self.state, self.TABLE, state_key, order_time)
            save_state(self.state)

            parsed = parse(order_time).date()
            if end_date is not None and parsed > end_date:
                LOGGER.info("Synced past the specified end_date ({}) - quitting".format(parsed))
                return None, orders

        next_token = raw_orders.parsed.get('NextToken', {}).get('value')
        return next_token, orders
