import pandas as pd
import unittest

from alva.machine_learning.data import features


class FeaturesHelper(unittest.TestCase):
    def setUp(self):
        self.data_test = pd.DataFrame({
            "price": [
                112000, 55000, 66000,
                200000, 144000, 33000
            ],
            "price_sqrm": [
                1000, 1050, 1200,
                1300, 1500, 800
            ],
            "district": [
                'Lozenets', 'Iztok', 'Mladost 4',
                'Dianabad', 'Musagenitsa', 'Ivan Vazov'
            ]
        })

    def test_add_average_discount_to_target(self):
        data = features.add_average_discount_to_target(self.data_test)
        adj_price_sample = data.iloc[0]['adj_price_sqrm']
        self.assertEqual(adj_price_sample, 950.0)

    def test_add_park_district_feature(self):
        data = features.add_park_district_feature(self.data_test)
        has_park = data.iloc[4]['park_district']
        self.assertFalse(has_park)
