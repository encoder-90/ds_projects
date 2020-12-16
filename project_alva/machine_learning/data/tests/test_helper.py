import pandas as pd
import unittest

from alva.machine_learning.data import helper


class TestHelper(unittest.TestCase):
    def setUp(self):
        column_names = ["apartment_type", "district", "price", "sqr_m", "price_sqrm",
                        "currency", "year", "floor", "gas", "heating", "construction_type",
                        "furnished", "entrance_control", "security", "passageway"]
        self.data = pd.read_csv("../../../scraper/offers.csv", names=column_names, header=None)

    def test_load_scraper_data(self):
        column_names = ["apartment_type", "district", "price", "sqr_m", "price_sqrm",
                        "currency", "year", "floor", "gas", "heating", "construction_type",
                        "furnished", "entrance_control", "security", "passageway"]

        self.assertListEqual(column_names, self.data.columns.values.tolist())

    def test_remove_missing_values(self):
        data = helper.remove_missing_values(self.data)
        missing_price = data.price.isnull().sum()
        self.assertEqual(missing_price, 0)

    def test_add_most_frequent_value_for_missing_columns(self):
        year_mode = int(self.data.year.mode())
        floor_mode = int(self.data.floor.mode())
        self.data = helper.add_most_frequent_value_for_missing_columns(self.data)
        year_mode_update = int(self.data.year.mode())
        floor_mode_update = int(self.data.floor.mode())
        self.assertEqual(year_mode, year_mode_update)
        self.assertEqual(floor_mode, floor_mode_update)

    def test_map_construction_type_to_en(self):
        data = helper.map_construction_type_to_en(self.data)
        found = data[data['construction_type'].str.contains('Тухла')].empty
        self.assertTrue(found)
