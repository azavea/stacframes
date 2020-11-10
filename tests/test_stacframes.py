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
            "properties": [{"catalog": "one"}, {"catalog": "one"}, {"catalog": "two"}],
        }
        df = gpd.GeoDataFrame(d, crs="EPSG:4326")
        catalog = pystac.Catalog("test", "test")
        stacframes.df_to(catalog, df, parents=["catalog"])
        self.assertEqual(len(list(catalog.get_children())), 2)
        catalog_one = catalog.get_child("test-one")
        self.assertEqual(len(list(catalog_one.get_items())), 2)
        self.assertEqual(catalog_one.extent.spatial.bboxes, [bbox])
        self.assertEqual(catalog_one.extent.temporal.intervals, [[dt, dt]])
        catalog_two = catalog.get_child("test-two")
        self.assertEqual(len(list(catalog_two.get_items())), 1)
        self.assertEqual(catalog_two.get_item("c").id, "c")

    def test_nested_add_int_property(self):
        """Ensure we can use parents arg on properties that contain ints"""
        dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        geometry = box(0.0, 0.0, 1.0, 1.0)
        bbox = [*geometry.bounds]
        d = {
            "id": ["a", "b", "c"],
            "datetime": [dt, dt, dt],
            "geometry": [geometry, geometry, geometry],
            "bbox": [bbox, bbox, bbox],
            "properties": [{"year": 2000}, {"year": 2000}, {"year": 2010}],
        }
        df = gpd.GeoDataFrame(d, crs="EPSG:4326")
        catalog = pystac.Catalog("test", "test")
        stacframes.df_to(catalog, df, parents=["year"])
        self.assertEqual(len(list(catalog.get_children())), 2)
        catalog_one = catalog.get_child("test-2000")
        self.assertEqual(len(list(catalog_one.get_items())), 2)
        self.assertEqual(catalog_one.extent.spatial.bboxes, [bbox])
        self.assertEqual(catalog_one.extent.temporal.intervals, [[dt, dt]])
        catalog_two = catalog.get_child("test-2010")
        self.assertEqual(len(list(catalog_two.get_items())), 1)
        self.assertEqual(catalog_two.get_item("c").id, "c")
