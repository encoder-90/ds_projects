import pandas as pd
import numpy as np


def load_scraper_data():
    column_names = ["apartment_type", "district", "price", "sqr_m", "price_sqrm",
                    "currency", "year", "floor", "gas", "heating", "construction_type",
                    "furnished", "entrance_control", "security", "passageway"]

    # Change the path based on csv location and name
    data = pd.read_csv("shared_resources\\offers.csv", names=column_names, header=None)
    data = data.reset_index(drop=True)

    return data


def remove_missing_values(data):
    # Drop NaN values in price - can be changed for more columns
    data = data.dropna(subset=['price'])
    data = data.reset_index(drop=True)

    return data


def add_most_frequent_value_for_missing_columns(data):
    # Most frequent values imputer for missing data
    year_mode = int(data.year.mode())
    floor_mode = int(data.floor.mode())
    data['year'].replace({np.nan: year_mode}, inplace=True)
    data['floor'].replace({np.nan: floor_mode}, inplace=True)

    return data


def restructure_initial_data(data):
    # Fix data
    data['district'].replace({'Gotse Gelchev': 'Gotse Delchev'}, inplace=True)

    return data


def map_construction_type_to_en(data):
    mapping_type = {
        'Гредоред': 'Timbered',
        'ЕПК': 'EPK',
        'ПК': 'PK',
        'Панел': 'Panel',
        'Тухла': 'Brick'
    }

    # inplace for direct changes to the DataFrame
    data['construction_type'].replace(mapping_type, inplace=True)

    return data


def delete_columns_after_encoding(data):
    EXTRA_COLUMNS_TO_DELETE = [
        'apartment_type',
        'district',
        'price',
        'adj_price_sqrm',
        'region',
        'population',
        'construction_type',
        'currency',
        'price_sqrm'
    ]

    available_columns = list(data.columns)
    for extra_column in EXTRA_COLUMNS_TO_DELETE:
        if extra_column in available_columns:
            del data[extra_column]

    return data


def encode_categorical_dummies(data):
    dummy_1 = pd.get_dummies(data, columns=['apartment_type'])
    dummy_2 = pd.get_dummies(data, columns=['district'])
    dummy_3 = pd.get_dummies(data, columns=['construction_type'])
    dummy_4 = pd.get_dummies(data, columns=['region'])

    features_to_concat = [data, dummy_1, dummy_2, dummy_3, dummy_4]
    features = pd.concat(features_to_concat, axis=1)

    # delete the extra columns
    features = features.loc[:, ~features.columns.duplicated()]

    return features


def merge_two_data_frames(df1, df2):
    merged_df = pd.concat([df1, df2])
    merged_df = merged_df.reset_index(drop=True)

    return merged_df


def sample_random_data_for_tests(df_data):
    """"
    The method takes the enriched and encoded data from scraper, sample 10 random rows and exclude the
    price target column because we can use data_test to make predictions. The data frame compare_price is
    used later to check the predictions with the original target values.
    """
    data_test = df_data.sample(n=10)
    compare_price = data_test.copy()

    data_test = data_test.drop(columns=['adj_price'])
    data_test = data_test.reset_index(drop=True)

    df_data = df_data[~df_data.index.isin(compare_price.index)]

    return df_data, data_test, compare_price


def get_benchmark_df():
    data_check = {
        'apartment_type': [
            '3-STAEN', '2-STAEN', '2-STAEN', '3-STAEN', '3-STAEN', '2-STAEN', '3-STAEN', '3-STAEN'
        ],
        'district': [
            'Banishora', 'Hipodruma', 'Vrajdebna', 'Dragalevtsi', 'Lozenets', 'Moderno predgradie', 'Sveta Troica',
            'Geo Milev'
        ],
        'price': [
            125000.0, 95500.0, 61600.0, 184000.0, 196200.0, 66600.0, 112200.0, 150000.0
        ],
        'sqr_m': [
            125, 75, 77, 160, 109, 74, 102, 92.0
        ],
        'price_sqrm': [
            1000.0, 1273.33, 800.0, 1150.0, 1800.0, 900.0, 1100.0, 1630.0
        ],
        'currency': [
            'EUR', 'EUR', 'EUR', 'EUR', 'EUR', 'EUR', 'EUR', 'EUR'
        ],
        'year': [
            2019.0, 2018.0, 2021.0, 1994.0, 2020.0, 2009.0, 2019.0, 1960.0
        ],
        'floor': [
            7.0, 8.0, 4.0, 3.0, 4.0, 4.0, 3.0, 2.0
        ],
        'gas': [
            0, 0, 0, 0, 0, 0, 0, 0
        ],
        'heating': [
            1, 1, 0, 0, 0, 0, 0, 1
        ],
        'construction_type': [
            'Brick', 'Brick', 'Brick', 'Brick', 'Brick', 'Brick', 'Brick', 'Brick'
        ],
        'furnished': [
            0, 0, 0, 1, 0, 0, 0, 1
        ],
        'entrance_control': [
            1, 1, 0, 0, 1, 1, 1, 1
        ],
        'security': [
            0, 0, 0, 0, 1, 0, 0, 0
        ],
        'passageway': [
            0, 0, 0, 0, 0, 0, 0, 0
        ]
    }
    df_check = pd.DataFrame(data_check)
    # For checking the DataFrame
    # pd.options.display.max_columns = None
    # print(df_check)

    # Add 5% for discount later with scraper data - can be fixed after refactoring
    df_check['price'] = df_check.price.map(lambda x: (x + x * 0.05))
    df_check['price_sqrm'] = df_check.price_sqrm.map(lambda x: (x + x * 0.05))

    return df_check


def get_data_frame_for_prediction_test():
    data = {
        'apartment_type': ['3-STAEN'],
        'district': ['Lozenets'],
        'price': [184000.0],
        'sqr_m': [125],
        'price_sqrm': [1472.0],
        'currency': ['EUR'],
        'year': [1994.0],
        'floor': [4.0],
        'gas': [0],
        'heating': [1],
        'construction_type': ['Brick'],
        'furnished': [0],
        'entrance_control': [1],
        'security': [0],
        'passageway': [0]
    }
    df_test = pd.DataFrame(data)

    return df_test
