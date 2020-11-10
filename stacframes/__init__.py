from datetime import datetime
import geopandas as gpd
import pandas as pd
import pystac
from shapely.geometry import mapping, shape

from .parents import DEFAULT_PARENTS_COLUMN
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


def df_to(catalog, dataframe, parents_col=DEFAULT_PARENTS_COLUMN):
    """Add all items in dataframe to catalog



    Args:
        dataframe (pandas.DataFrame): A DataFrame of rows structured as described
            by stacframes.item_from.
        catalog (pystac.Catalog): The Catalog to add the items in dataframe to.
        parents_col (str): A column in dataframe that contains a list of
            collection ids to attach the item to. The collections are
            created in the pystac catalog tree if they do not exist.
            `stacframes.parents` contains a few helper methods for generating the
            parents column, and examples/aviris/main.py presents an example.

    """

    def handle_row(series):
        parents_list = series.get(parents_col, [])
        child_catalog = build_recursive(catalog, parents_list, "collection")
        item = item_from(series)
        child_catalog.add_item(item)

    dataframe.apply(handle_row, axis=1)

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
