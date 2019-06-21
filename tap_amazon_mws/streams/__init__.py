
from tap_amazon_mws.streams.orders import OrdersStream
from tap_amazon_mws.streams.inventory import InventoryStream
from tap_amazon_mws.streams.products import ProductStream

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
