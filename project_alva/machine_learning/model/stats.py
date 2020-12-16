import numpy as np
import pandas as pd

from alva.machine_learning.data import helper


def transform_target_y(data):
    """
    Transform the target column y to natural log. This scales the target and helps to stabilize the outcome
    by normally distributing the values.
    NOTE: It needs to transform back with exponential e = 2.71828
    """
    data.adj_price = np.log(data.adj_price)

    return data


def reverse_log_transformation(result_df):
    """
    https://numpy.org/doc/stable/reference/generated/numpy.exp.html
    """
    result_df.adj_price = np.exp(result_df.adj_price)
    result_df.model_price_prediction = np.exp(result_df.model_price_prediction)

    return result_df


def get_data_subset_for_district(district):
    """
    Data is cleaned, restructured and sliced base on the prediction district from the mapper data
    """
    data = helper.load_scraper_data()
    data = helper.restructure_initial_data(data)
    data = helper.remove_missing_values(data)
    data = helper.map_construction_type_to_en(data)
    district_data = data.loc[data['district'] == district]

    return district_data


def get_number_samples_mapper():
    """
    Delete missing target rows - price from scrapper data and returns the number of rows for the new DataFrame
    """
    data = helper.load_scraper_data()
    data = helper.remove_missing_values(data)
    rows = int(data.shape[0])

    return rows


def get_stats_for_apartment_type(data_filter, column_name):
    by_ap_type = data_filter.groupby('apartment_type')[column_name].mean()

    return by_ap_type


def get_bar_plot_figure_app_type(specific_data, prediction):  # data should be already filtered by district
    mean_price_dist = int(round(specific_data["price"].mean(), 0))

    mapping_type = {'1-STAEN': '1 ROOM', '2-STAEN': '2 ROOM', '3-STAEN': '3 ROOM', '4-STAEN': '4 ROOM',
                    'MNOGOSTAEN': '5+ ROOMS', 'MEZONET': '2+ FLOORS', 'ATELIE': 'STUDIO'}
    specific_data['apartment_type'].replace(mapping_type, inplace=True)

    plot_bar = specific_data.groupby("apartment_type").price.mean().sort_values(ascending=False).plot.bar(
        title='Your prediction comparison based on district', figsize=(10, 6))
    plot_bar.set_xlabel("APARTMENT TYPE")
    plot_bar.set_ylabel("PRICE")

    plot_bar.hlines(mean_price_dist, -.5, 6.5, linestyles='dashed', color='red')
    annot_word = (mean_price_dist * 0.05) + mean_price_dist
    plot_bar.annotate('average district price', (4.0, annot_word))

    plot_bar.hlines(prediction, -.5, 6.5, linestyles='dashed', color='green')
    annot_prediction = (prediction * 0.05) + prediction
    plot_bar.annotate('prediction price', (4.0, annot_prediction))

    fig = plot_bar.get_figure()
    fig.savefig('prediction.png',  bbox_inches='tight')


# data = get_data_subset_for_district(district='Lozenets')
# prediction = 111111
# get_bar_plot_figure_app_type(data, prediction)

# fig = get_bar_plot_figure_app_type(data)
# print(fig)
# data = get_stats_for_apartment_type(data, 'price_sqrm')
# print(data)
# print(get_number_samples_mapper())