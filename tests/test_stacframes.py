from datetime import datetime, timezone
import unittest

import geopandas as gpd
import pandas as pd
import pystac
from shapely.geometry import box, mapping

import stacframes


class TestStacFramesManager(unittest.TestCase):
    def test_item_from(self):
        dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        geometry = box(0.0, 0.0, 1.0, 1.0)
        series = pd.Series(
            {
                "id": "foo",
                "geometry": geometry,
                "bbox": list(geometry.bounds),
                "properties": {},
                "datetime": dt,
                "links": [],
                "assets": {},
            },
        )
        item = stacframes.item_from(series)
        self.assertEqual(item.id, "foo")
        self.assertEqual(item.datetime, dt)
        self.assertEqual(
            item.geometry,
            {
                "coordinates": (
                    ((1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0), (1.0, 0.0)),
                ),
                "type": "Polygon",
            },
        )
        self.assertEqual(item.bbox, [0.0, 0.0, 1.0, 1.0])

    def test_series_from(self):
        dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        geometry = box(0.0, 0.0, 1.0, 1.0)
        item = pystac.Item("foo", mapping(geometry), geometry.bounds, dt, {})
        series = stacframes.series_from(item)
        self.assertEqual(series["id"], item.id)
        self.assertEqual(series["geometry"], geometry)
        self.assertEqual(series["bbox"], geometry.bounds)
        self.assertEqual(series["datetime"], dt)

    def test_flat_add(self):
        """Ensure add works with no parents arg"""
        dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        geometry = box(0.0, 0.0, 1.0, 1.0)
        bbox = [*geometry.bounds]
        d = {
            "id": ["a", "b", "c"],
            "datetime": [dt, dt, dt],
            "geometry": [geometry, geometry, geometry],
            "bbox": [bbox, bbox, bbox],
        }
        df = gpd.GeoDataFrame(d, crs="EPSG:4326")
        catalog = pystac.Catalog("test", "test")
        stacframes.df_to(catalog, df)
        self.assertEqual(len(list(catalog.get_children())), 0)
        self.assertEqual(len(list(catalog.get_items())), 3)

    def test_nested_add(self):
        """Ensure parents arg generates nested collections"""
        dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        geometry = box(0.0, 0.0, 1.0, 1.0)
        bbox = [*geometry.bounds]
        d = {
            "id": ["a", "b", "c"],
            "datetime": [dt, dt, dt],
            "geometry": [geometry, geometry, geometry],
            "bbox": [bbox, bbox, bbox],
            "properties": [{}, {}, {}],
            "parents": [[], ["foo"], ["foo", "bar"]],
        }
        df = gpd.GeoDataFrame(d, crs="EPSG:4326")
        catalog = pystac.Catalog("test", "test")
        stacframes.df_to(catalog, df)
        self.assertEqual(len(list(catalog.get_children())), 1)
        catalog_foo = catalog.get_child("foo")
        self.assertEqual(len(list(catalog_foo.get_items())), 1)
        self.assertEqual(catalog_foo.extent.spatial.bboxes, [bbox])
        self.assertEqual(catalog_foo.extent.temporal.intervals, [[dt, dt]])
        catalog_bar = catalog_foo.get_child("bar")
        self.assertEqual(len(list(catalog_bar.get_items())), 1)
        self.assertEqual(catalog_bar.get_item("c").id, "c")
