# STACFrames

A Python library for working with STAC Catalogs via Pandas DataFrames

## Installation

Install via pip:

```shell
pip install stacframes
```

## Usage

To load a STAC Catalog into a GeoDataFrame:

```python
import pystac
import stacframes

catalog = pystac.Catalog.from_file("path/to/catalog.json")
df = stacframes.to_df(catalog)
```

To write a DataFrame to a STAC Catalog:

```python
from datetime import datetime, timezone
import pandas as pd
import pystac
from shapely.geometry import box
import stacframes

df = pd.read_csv("path/to/data.csv")

# Filter, map, edit dataframe as desired

# Map dataframe rows
def map_row_to_item(series):

    # Get and transform necessary column values from series
    geometry = series["geom"]
    dt = series["event_time"]

    return {
      "id": series["uuid"]
      "geometry": geometry
      "bbox": list(geometry.bounds)
      "datetime": dt
    }

df = df.apply(map_row_to_item)
catalog = pystac.Catalog("data", "My Data")
stacframes.add(df, catalog)
catalog.normalize_and_save("./path/to/catalog.json")
```

Please take a look at [the source code](https://github.com/azavea/stacframes/blob/master/stacframes/__init__.py) for more examples and additional documentation.

## Developing

Install the development requirements:

```shell
pip install -r requirements-dev.txt
```

Make changes as desired, then run:

```shell
./scripts/test
```

## Releasing a new version

Follow the checklist in [RELEASE.md](./RELEASE.md)
