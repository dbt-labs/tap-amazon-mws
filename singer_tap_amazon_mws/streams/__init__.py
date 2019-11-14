
from singer_tap_amazon_mws.streams.orders import OrdersStream
from singer_tap_amazon_mws.streams.inventory import InventoryStream
from singer_tap_amazon_mws.streams.products import ProductStream

AVAILABLE_STREAMS = [
    OrdersStream,
    InventoryStream,
    ProductStream
]

__all__ = [
    'OrdersStream',
    'InventoryStream',
    'ProductStream',
]
