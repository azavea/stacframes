import unittest

import pandas as pd

from stacframes.parents import from_properties, from_properties_accum


class TestFromPropertiesManager(unittest.TestCase):
    def test_error_if_has_parents_col(self):
        parents_col = "parents"
        df = pd.DataFrame(
            {
                "id": ["a"],
                "properties": [{"foo", "bar"}],
                parents_col: [["cannot", "exist"]],
            }
        )
        with self.assertRaises(ValueError):
            df = from_properties(["foo"], df, parents_col=parents_col)

    def test_error_if_no_properties(self):
        parents_col = "parents"
        df = pd.DataFrame({"id": ["a"]})
        with self.assertRaises(ValueError):
            df = from_properties(["foo"], df, parents_col=parents_col)

    def test_from_properties(self):
        df = pd.DataFrame({"id": ["a"], "properties": [{"foo": "bar", "baz": 123}]})
        df = from_properties(["foo", "baz"], df)
        self.assertEqual(len(df["parents"]), 1)
        self.assertEqual(df["parents"][0], ["bar", "123"])

    def test_from_properties_prefix(self):
        df = pd.DataFrame({"id": ["a"], "properties": [{"foo": "bar", "baz": 123}]})
        df = from_properties(["foo", "baz"], df, prefix="prefix-")
        self.assertEqual(len(df["parents"]), 1)
        self.assertEqual(df["parents"][0], ["prefix-bar", "prefix-123"])


class TestFromPropertiesAccumManager(unittest.TestCase):
    def test_error_if_has_parents_col(self):
        df = pd.DataFrame({"parents": ["foo", "bar"]})
        with self.assertRaises(ValueError):
            from_properties_accum(["foo"], df)

    def test_error_if_no_properties(self):
        df = pd.DataFrame({})
        with self.assertRaises(ValueError):
            from_properties_accum(["foo"], df)

    def test_from_properties_accum(self):
        df = pd.DataFrame({"properties": [{"Year": 2020, "Month": 1}]})
        df = from_properties_accum(["Year", "Month"], df)
        self.assertEqual(df["parents"][0], ["2020", "20201"])

    def test_from_properties_accum_prefix(self):
        df = pd.DataFrame({"properties": [{"Year": 2020, "Month": 1}]})
        df = from_properties_accum(["Year", "Month"], df, prefix="dt", separator="-")
        self.assertEqual(df["parents"][0], ["dt-2020", "dt-2020-1"])

    def test_from_properties_accum_separator(self):
        df = pd.DataFrame({"properties": [{"Year": 2020, "Month": 1}]})
        df = from_properties_accum(["Year", "Month"], df, separator="-")
        self.assertEqual(df["parents"][0], ["2020", "2020-1"])
