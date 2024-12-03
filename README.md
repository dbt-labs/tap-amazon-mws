# ***Archival Notice***
This repository has been archived.

As a result all of its historical issues and PRs have been closed.

Please *do not clone* this repo without understanding the risk in doing so:
- It may have unaddressed security vulnerabilities
- It may have unaddressed bugs

<details>
   <summary>Click for historical readme</summary>

# tap-amazon-mws

Author: Drew Banin (drew@fishtownanalytics.com)

This is a [Singer](http://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

It:

- Generates a catalog of available data in the Amazon MWS API
- Extracts the following resources:
    - Orders
    - OrderItems

### Quick Start

1. Install

```bash
git clone git@github.com:fishtown-analytics/tap-amazon-mws.git
cd tap-amazon-mws
pip install .
```

2. Get credentials from Amazon

The following credentials are required:
 - access_key
 - secret_key
 - seller_id
 - region
 - marketplace_ids

See the section on creating a config file below for more information about these credentials.


3. Create the config file.

There is a template you can use at `config.json.example`, just copy it to `config.json` in the repo root and insert your credentials.

4. Run the application to generate a catalog.

```bash
tap-amazon-mws -c config.json -d > catalog.json
```

5. Select the tables you'd like to replicate

Step 4 a file called `catalog.json` that specifies all the available endpoints and fields. You'll need to open the file and select the ones you'd like to replicate. See the [Singer guide on Catalog Format](https://github.com/singer-io/getting-started/blob/c3de2a10e10164689ddd6f24fee7289184682c1f/BEST_PRACTICES.md#catalog-format) for more information on how tables are selected.

6. Run it!

```bash
tap-amazon-mws -c config.json --catalog catalog.json
```

Copyright &amp;copy; 2019 Fishtown Analytics

