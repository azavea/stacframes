from datetime import datetime
import geopandas as gpd
import pandas as pd
import pystac
from shapely.geometry import mapping, shape

from .utils import build_recursive, update_collection_extents


def item_from(series):
    """Convert series to pystac.Item

    series must have at least the following columns:
        - id (str)
        - geometry (shapely.Geometry)
        - bbox ([float, float, float, float])
        - datetime (datetime.datetime)

    It may optionally have the following columns:
        - assets (dict)
        - links (list)
        - properties (dict)

    If you wish to encode STAC Assets and Links it is recommended that you construct
    the actual pystac objects in your code and then call `to_dict()` on them before
    adding them to your dataframe. For example:
    ```
    series["assets"] = {"asset_id": pystac.Asset(...).to_dict()}
    ```


    Args:
        - series (pandas.Series)

    Returns:
        pystac.Item

    Note:
        Ensure your geometry column is reprojected to EPSG:4326 prior to use
    """
    series_dict = series.to_dict()

    series_dict.setdefault("stac_version", pystac.get_stac_version())
    series_dict.setdefault("type", "Feature")
    series_dict.setdefault("assets", {})
    series_dict.setdefault("links", [])
    series_dict.setdefault("properties", {})

    dt = series_dict.get("datetime", None)
    if dt and series_dict["properties"].get("datetime", None) is None:
        dt_str = pystac.utils.datetime_to_str(dt) if isinstance(dt, datetime) else dt
        series_dict["properties"]["datetime"] = dt_str
        del series_dict["datetime"]

    series_dict["geometry"] = mapping(series_dict["geometry"])
    # from_dict handles associating any Links and Assets with the Item
    return pystac.Item.from_dict(series_dict)


def series_from(item):
    """Convert item to a pandas.Series

    The Series will at minimum contain the following columns:
        - id (str)
        - geometry (shapely.Geometry)
        - bbox (list[float, float, float, float])
        - datetime (datetime.datetime)

    item.properties["datetime"] is promoted to its own column as a
    datetime object if available.

    Args:
        item (pystac.Item): STAC Item to be converted.

    Returns:
        pandas.Series

    """
    item_dict = item.to_dict()
    item_id = item_dict["id"]

    # Promote datetime
    dt = item_dict["properties"]["datetime"]
    item_dict["datetime"] = pystac.utils.str_to_datetime(dt)
    del item_dict["properties"]["datetime"]

    # Convert geojson geom into shapely.Geometry
    item_dict["geometry"] = shape(item_dict["geometry"])

    return pd.Series(item_dict, name=item_id)


def add(pd_dataframe, catalog, parents=None):
    """Add all items in pd_dataframe to catalog

    Args:
        pd_dataframe (pandas.DataFrame): A DataFrame of rows structured as described
            by stacframes.item_from.
        catalog (pystac.Catalog): The Catalog to add the items in pd_dataframe to.
        parents (list): An ordered list of column names on the passed dataframe.
            This method will retrieve the value of the column for each item
            in order and add the Item to Collections named by the value in the Item
            column. See tests/test_stacframes.py for examples.

    """

    def handle_row(series):
        props = series.get("properties", {})
        parent_values = [props[v] for v in parents]
        child_catalog = build_recursive(catalog, parent_values, "collection")
        item = item_from(series)
        child_catalog.add_item(item)

    if not parents:
        parents = []
    pd_dataframe.apply(handle_row, axis=1)

    update_collection_extents(catalog)


def df_from(catalog, crs="EPSG:4326"):
    """Read catalog into a new geopandas.GeoDataFrame

    Reprojects GeoDataFrame to the provided crs

    Args:
        catalog (pystac.Catalog): The Catalog to read STAC Items from.
        crs (any): Optional. Value can be anything accepted by
            http://pyproj4.github.io/pyproj/stable/api/crs/crs.html#pyproj.crs.CRS.from_user_input

    Returns:
        geopandas.GeoDataFrame

    """
    series = [series_from(item) for item in catalog.get_all_items()]
    return gpd.GeoDataFrame(series, crs=crs)
