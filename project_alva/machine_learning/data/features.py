from alva import mapping


def add_average_discount_to_target(data):
    """
    adjust the price (target) with -5% in a new columns adj_price and adj_price_sqrm
    """

    data['adj_price'] = data.price.map(lambda x: (x - x * 0.05))
    data['adj_price_sqrm'] = data.price_sqrm.map(lambda x: (x - x * 0.05))

    return data


def add_park_district_feature(data):
    """
    Additional column park_district: True if there is a park in the district (or near the border of it)
    False otherwise.
    """

    data.loc[:, 'park_district'] = data.loc[:, 'district'].apply(
        lambda x: mapping.SOFIA_NEIGHBOURHOOD_PARK_TRUE_FALSE_MAPPING[x]
    )

    return data


def add_region_feature(data):
    """
    Additional column for the region - needed for mapping the population, green areas etc.
    """

    data.loc[:, 'region'] = data.loc[:, 'district'].apply(
        lambda x: mapping.SOFIA_NEIGHBOURHOOD_TO_REGION_MAPPING[x]
    )

    return data


def add_population_feature(data):
    """
    The population is divided into regions in Sofia. The last available data was in 2011 that shows that
    between 2001 and 2011 the population growth was a little more than 10 % average for all the districts.
    This means that we will adjust the number by +10% before the next population count in 2021.
    """

    data.loc[:, 'population'] = data.loc[:, 'region'].apply(
        lambda x: mapping.SOFIA_REGIONS_POPULATION_MAPPING[x]
    )
    data['adj_population'] = data.population.map(lambda x: (x + x * 0.1))

    return data


def add_green_areas_feature(data):
    # TODO filter the green area mapper for more accurate values

    data.loc[:, 'green_area'] = data.loc[:, 'region'].apply(
        lambda x: mapping.SOFIA_REGIONS_GREEN_MAPPING[x]
    )

    return data


def add_supermarkets_feature(data):
    """
    Additional column for counting the big supermarkets per district.
    """
    data.loc[:, 'nr_supermarkets'] = data.loc[:, 'district'].apply(
        lambda x: mapping.SOFIA_NEIGHBOURHOOD_SUPERMARKET_MAPPING[x])

    return data


def add_metro_feature(data):
    """
    Additional bool column for metro station in district.
    """
    data.loc[:, 'has_metro'] = data.loc[:, 'district'].apply(
        lambda x: mapping.SOFIA_METRO_TRUE_FALSE_MAPPING[x])

    return data


def add_hospital_feature(data):
    """
    Additional bool column for hospitals in each district.
    """
    data.loc[:, 'has_hospital'] = data.loc[:, 'district'].apply(
        lambda x: mapping.SOFIA_HOSPITALS_TRUE_FALSE_MAPPING[x])

    return data
