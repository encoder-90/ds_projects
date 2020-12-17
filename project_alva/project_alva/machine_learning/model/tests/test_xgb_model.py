import pickle
import re
import unittest
import pandas as pd
import xgboost as xgb
import numpy as np


from alva.machine_learning.model import xgb_model
from alva.machine_learning.data import helper


class TestXgbModel(unittest.TestCase):
    def setUp(self):
        column_names = ["apartment_type", "district", "price", "sqr_m", "price_sqrm",
                        "currency", "year", "floor", "gas", "heating", "construction_type",
                        "furnished", "entrance_control", "security", "passageway"]
        self.data = pd.read_csv("../../../scraper/offers.csv", names=column_names, header=None)
        self.data = xgb_model.preparing_data(self.data)  # This step can be mocked
        self.has_discount = True

        with open('../model_pickle', 'rb') as f:
            self.model = pickle.load(f)

    def test_enrich_data(self):
        """
        Checks if all the features are successfully added to the initial data
        """
        data = xgb_model.enrich_data(self.data, self.has_discount)
        self.assertEqual(len(data.columns), 25)

    def test_encode_data(self):
        """
        Checks if the number of columns after encoding is the same value as needed for the model training
        """
        data = xgb_model.enrich_data(self.data, self.has_discount)  # This step can be mocked
        data = xgb_model.encode_data(data)
        self.assertEqual(len(data.columns), 163)

    def test_load_model_from_pickle(self):
        """
        Check if the model saved(serialized) as pickle object is an instance of XGBoost model
        """
        error_message_regex = r'.+class.+\'xgboost.core.Booster.+'
        model_str = str(type(self.model))
        match = re.search(error_message_regex, model_str)
        self.assertIs(model_str, match.group(0))

    def test_make_prediction_web_app(self):
        """
        Uses test data from machine_learning.data.helper to test the model prediction function
        """
        web_data = helper.get_data_frame_for_prediction_test()
        merged_df = helper.merge_two_data_frames(web_data, self.data)
        merged_df = xgb_model.data_wrangling_cycle(merged_df)
        df_web_data = merged_df.head(1)
        df_web_data = df_web_data.drop(columns=['adj_price'])
        to_predict = xgb.DMatrix(df_web_data.values, feature_names=df_web_data.columns)
        prediction = np.exp(self.model.predict(to_predict))
        prediction = int(round(prediction[0], 0))
        self.assertIsNotNone(prediction)
