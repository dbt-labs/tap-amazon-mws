#!/usr/bin/env python3

import singer

import tap_framework

from tap_amazon_mws.client import AmazonMWSClient
from tap_amazon_mws.streams import AVAILABLE_STREAMS

LOGGER = singer.get_logger()  # noqa


class AmazonMWSRunner(tap_framework.Runner):
    pass


@singer.utils.handle_top_exception(LOGGER)
def main():
    args = singer.utils.parse_args(
        required_config_keys=['access_key', 'secret_key', 'seller_id',
                              'region', 'marketplace_ids', 'start_date'])

    client = AmazonMWSClient(args.config)
    runner = AmazonMWSRunner(
        args, client, AVAILABLE_STREAMS)

    if args.discover:
        runner.do_discover()
    else:
        runner.do_sync()


if __name__ == '__main__':
    main()
