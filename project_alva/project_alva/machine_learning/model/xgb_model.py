import pickle
import xgboost as xgb
import pandas as pd
import numpy as np

# from sklearn.metrics import mean_squared_error
# from sklearn.model_selection import train_test_split

# from alva.machine_learning.data import helper
from machine_learning.data import helper
# from alva.machine_learning.data import features
from machine_learning.data import features
# from alva.machine_learning.model import stats
from machine_learning.model import stats


def preparing_data(data):
    data_prep = data.copy()
    data_prep = helper.remove_missing_values(data_prep)
    # NOTE: we don't impute the most frequent values for year/floor because Xgboost has a build-in function for nan's
    data_prep = helper.restructure_initial_data(data_prep)
    data_prep = helper.map_construction_type_to_en(data_prep)

    return data_prep


def enrich_data(data, has_discount):  # Use this method for feature engineering
    enr_data = data.copy()
    if has_discount:
        enr_data = features.add_average_discount_to_target(enr_data)

    enr_data = features.add_park_district_feature(enr_data)
    enr_data = features.add_region_feature(enr_data)
    enr_data = features.add_population_feature(enr_data)
    enr_data = features.add_green_areas_feature(enr_data)
    enr_data = features.add_metro_feature(enr_data)
    enr_data = features.add_supermarkets_feature(enr_data)
    enr_data = features.add_hospital_feature(enr_data)

    return enr_data


def encode_data(data):
    code_data = data.copy()
    code_data = helper.encode_categorical_dummies(code_data)
    code_data = helper.delete_columns_after_encoding(code_data)

    return code_data


def data_wrangling_cycle(df_data):
    merged_df = df_data.copy()
    # Prepare merge data for enrichment
    merged_df = preparing_data(merged_df)
    # Data enrichment
    has_discount = True
    merged_df = enrich_data(merged_df, has_discount)
    # Data encoding
    merged_df = encode_data(merged_df)

    return merged_df


def train_model_xgboost(data):
    df_data = data.copy()

    # Transform target y
    df_data = stats.transform_target_y(df_data)

    # Split the data and train the model
    X = df_data.drop(columns=['adj_price']).copy()
    y = df_data.adj_price

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15)
    xgboost_parameters = {
        'early_stopping_rounds': 100,
        'num_boost_round': 2000,
        'verbose_eval': False,
        'params': {
            'max_depth': 6,
            'eval_metric': 'rmse',
            'objective': 'reg:linear',
            'eta': 0.05,
            'nthread': 4,
            'silent': True,
        }
    }

    train_d = xgb.DMatrix(X_train.values, label=y_train, feature_names=X_train.columns)
    watch_list = [(train_d, 'train')]

    eval_d = xgb.DMatrix(X_test.values, label=y_test, feature_names=X_test.columns)
    watch_list += [(eval_d, 'eval')]

    evals_result_data = {}
    model = xgb.train(dtrain=train_d, evals=watch_list, evals_result=evals_result_data, **xgboost_parameters)

    X_test = xgb.DMatrix(X_test.values, label=y_test, feature_names=X_test.columns)
    y_pred = model.predict(X_test)

    # For Regression model evaluation
    mse = mean_squared_error(y_test, y_pred)
    mse_str = "MSE: " + str(mse)
    rmse_str = "RMSE: " + str(np.sqrt(mse))

    return model, mse_str, rmse_str


def save_model_to_pickle(model):
    with open('shared_resources\\model_pickle', 'wb') as f:
        pickle.dump(model, f)


def load_model_from_pickle():
    with open('shared_resources\\model_pickle', 'rb') as f:
        model = pickle.load(f)

    return model


def get_testing_and_comparing_data_from_benchmark():
    # Load the data
    data_test = helper.get_benchmark_df()
    data = helper.load_scraper_data()
    # Merge the data
    merged_df = helper.merge_two_data_frames(data_test, data)
    # Prepare, enrich and encode the data
    merged_df = data_wrangling_cycle(merged_df)
    # Slice only the test data
    df_benchmark = merged_df.loc[0:7, :]
    # Transform target y
    df_benchmark = stats.transform_target_y(df_benchmark)
    # Two data frames for comparison
    compare_price = df_benchmark.copy()
    data_test = df_benchmark.drop(columns=['adj_price'])

    return data_test, compare_price


def make_prediction_web_app(web_data_django):  # TODO use this method as an API for prediction in Django
    # Load the model from file
    model = load_model_from_pickle()
    # Load the scraper data
    scraper_data = helper.load_scraper_data()
    # Merge the data
    merged_df = helper.merge_two_data_frames(web_data_django, scraper_data)
    # Prepare, enrich and encode the data
    merged_df = data_wrangling_cycle(merged_df)
    # Slice only the django data for prediction
    df_web_data = merged_df.head(1)
    df_web_data = df_web_data.drop(columns=['adj_price'])

    # Use the model for prediction
    to_predict = xgb.DMatrix(df_web_data.values, feature_names=df_web_data.columns)
    prediction = np.exp(model.predict(to_predict))
    prediction = int(round(prediction[0], 0))

    return prediction


def run():
    # Load the data
    data = helper.load_scraper_data()

    # Data wrangling
    data = preparing_data(data)

    # Data enrichment
    has_discount = True
    data = enrich_data(data, has_discount)

    # Encode data
    data = encode_data(data)

    # Build model
    model, mse, rmse = train_model_xgboost(data)
    # Get testing data
    data_test, compare_price = get_testing_and_comparing_data_from_benchmark()

    # Test model
    to_predict = xgb.DMatrix(data_test.values, feature_names=data_test.columns)
    compare_price.loc[:, 'model_price_prediction'] = list(model.predict(to_predict))
    result_df = compare_price[['model_price_prediction', 'adj_price']]

    # Reverse y transformation and prediction
    result_df = stats.reverse_log_transformation(result_df)

    pred_price_model = sum(list(result_df.loc[:, 'model_price_prediction']))
    actual_price = sum(list(result_df.loc[:, 'adj_price']))
    difference_model_actual = pred_price_model - actual_price
    print('Predicted Price: ' + str(round(pred_price_model, 0)))
    print('Actual Price: ' + str(actual_price))
    print('Difference:')
    print('Model Prediction - Actual Price: ' + str(round(difference_model_actual, 0)))

    print(result_df)
    print(mse)
    print(rmse)

    # Save model with test DataFrame
    # save_model_to_pickle(model)  # To unpack pickle use load_model_from_pickle()
    # data_test.to_pickle('data_test.pkl')
    # compare_price.to_pickle('comp_price.pkl')

# Save new instance of the XGBoost model # TODO make a unit test for this check
# run()

# Test if the model is accepting new data and making predictions # TODO make an integration test for this check
# web_data = helper.get_data_frame_for_prediction_test()
# pred = make_prediction_web_app(web_data)
# print(pred)
