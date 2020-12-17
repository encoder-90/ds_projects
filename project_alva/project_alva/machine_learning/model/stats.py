import numpy as np
import uuid
import pygal

from machine_learning.data import helper


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


def get_svg_bar_plot_district_mean_price_per_apartment_type(df_district, prediction_price):
    mapping_type = {'1-STAEN': '1 ROOM', '2-STAEN': '2 ROOM', '3-STAEN': '3 ROOM', '4-STAEN': '4 ROOM',
                    'MNOGOSTAEN': '5+ ROOMS', 'MEZONET': 'PENTHOUSE', 'ATELIE': 'STUDIO'}
    df_district['apartment_type'].replace(mapping_type, inplace=True)

    mean_price_studio = 0
    df_studio = df_district.loc[df_district['apartment_type'] == 'STUDIO']
    if len(df_studio.index) != 0: mean_price_studio = int(round(df_studio["price"].mean(), 0))

    mean_price_one_room = 0
    df_one_room = df_district.loc[df_district['apartment_type'] == '1 ROOM']
    if len(df_one_room.index) != 0: mean_price_one_room = int(round(df_one_room["price"].mean(), 0))

    mean_price_two_room = 0
    df_two_room = df_district.loc[df_district['apartment_type'] == '2 ROOM']
    if len(df_two_room.index) != 0: mean_price_two_room = int(round(df_two_room["price"].mean(), 0))

    mean_price_three_room = 0
    df_three_room = df_district.loc[df_district['apartment_type'] == '3 ROOM']
    if len(df_three_room.index) != 0: mean_price_three_room = int(round(df_three_room["price"].mean(), 0))

    mean_price_four_room = 0
    df_four_room = df_district.loc[df_district['apartment_type'] == '4 ROOM']
    if len(df_four_room.index) != 0: mean_price_four_room = int(round(df_four_room["price"].mean(), 0))

    mean_price_five_room = 0
    df_five_plus_room = df_district.loc[df_district['apartment_type'] == '5+ ROOMS']
    if len(df_five_plus_room.index) != 0: mean_price_five_room = int(round(df_five_plus_room["price"].mean(), 0))

    mean_price_penthouse = 0
    df_penthouse = df_district.loc[df_district['apartment_type'] == 'PENTHOUSE']
    if len(df_penthouse.index) != 0: mean_price_penthouse = int(round(df_penthouse["price"].mean(), 0))

    bar_chart = pygal.Bar(legend_at_bottom=True)
    bar_chart.title = 'Prediction value and district average price per apartment type (in €)'

    bar_chart.add('Your Prediction', [prediction_price])
    bar_chart.add('Studio', [mean_price_studio])
    bar_chart.add('One Room', [mean_price_one_room])
    bar_chart.add('Two Room', [mean_price_two_room])
    bar_chart.add('Three Room', [mean_price_three_room])
    bar_chart.add('Four Room', [mean_price_four_room])
    bar_chart.add('Five Plus Room', [mean_price_five_room])
    bar_chart.add('Penthouse', [mean_price_penthouse])

    file_name = f"prediction_bar{str(uuid.uuid4())}.svg"
    file_location = f"web_app\\static\\web_app\\media\\{file_name}"
    bar_chart.render_to_file(file_location)

    return file_name


def get_svg_pie_chart_by_number_properties_for_sale(df_district):
    mapping_type = {'1-STAEN': '1 ROOM', '2-STAEN': '2 ROOM', '3-STAEN': '3 ROOM', '4-STAEN': '4 ROOM',
                    'MNOGOSTAEN': '5+ ROOMS', 'MEZONET': 'PENTHOUSE', 'ATELIE': 'STUDIO'}
    df_district['apartment_type'].replace(mapping_type, inplace=True)

    count_studio = 0
    df_studio = df_district.loc[df_district['apartment_type'] == 'STUDIO']
    if len(df_studio.index) != 0: count_studio = df_studio["price"].count()

    count_one_room = 0
    df_one_room = df_district.loc[df_district['apartment_type'] == '1 ROOM']
    if len(df_one_room.index) != 0: count_one_room = df_one_room["price"].count()

    count_two_room = 0
    df_two_room = df_district.loc[df_district['apartment_type'] == '2 ROOM']
    if len(df_two_room.index) != 0: count_two_room = df_two_room["price"].count()

    count_three_room = 0
    df_three_room = df_district.loc[df_district['apartment_type'] == '3 ROOM']
    if len(df_three_room.index) != 0: count_three_room = df_three_room["price"].count()

    count_four_room = 0
    df_four_room = df_district.loc[df_district['apartment_type'] == '4 ROOM']
    if len(df_four_room.index) != 0: count_four_room = df_four_room["price"].count()

    count_five_room = 0
    df_five_plus_room = df_district.loc[df_district['apartment_type'] == '5+ ROOMS']
    if len(df_five_plus_room.index) != 0: count_five_room = df_five_plus_room["price"].count()

    count_penthouse = 0
    df_penthouse = df_district.loc[df_district['apartment_type'] == 'PENTHOUSE']
    if len(df_penthouse.index) != 0: count_penthouse = df_penthouse["price"].count()

    pie_chart = pygal.Pie(inner_radius=.4, show_legend=False)
    pie_chart.title = 'Number properties for sale per apartment type for your prediction district'
    pie_chart.add('Prediction placeholder', [0])
    pie_chart.add('Studio', [count_studio])
    pie_chart.add('One Room', [count_one_room])
    pie_chart.add('Two Room', [count_two_room])
    pie_chart.add('Three Room', [count_three_room])
    pie_chart.add('Four Room', [count_four_room])
    pie_chart.add('Five Plus Room', [count_five_room])
    pie_chart.add('Penthouse', [count_penthouse])

    file_name = f"prediction_pie{str(uuid.uuid4())}.svg"
    file_location = f"web_app\\static\\web_app\\media\\{file_name}"

    pie_chart.render_to_file(file_location)
    return file_name





