import requests
from requests import get
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
from time import sleep
from random import randint
import re


def scrape_by_url(url, apartment_type, district, pages):
    """
    Scrape web pages by given url as a start point.
    Pages determines outer loop length.
    """
    # data storage
    price = []
    price_sqrm = []
    sqr_m = []
    year_built = []
    floor = []
    construction_type = []
    furnished = []
    entrance_control = []
    security = []
    passageway = []
    gas = []
    heating = []

    current_page = 1
    pages_skipped = 0
    offers_skipped = 0

    while current_page <= pages:
        try:
            results = requests.get(url)
        except requests.exceptions.Timeout as e:
            # Maybe set up for a retry, or continue in a retry loop
            print("Connection Timeout: {}. Skipping to next page.".format(e))
            pages_skipped = pages_skipped + 1
            continue
        except requests.exceptions.TooManyRedirects as e:
            # Tell the user their URL was bad and try a different one
            print("Too many redirects: {}. Skipping next page".format(e))
            pages_skipped = pages_skipped + 1
            continue
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            raise SystemExit(e)
        # Use results.content - https://stackoverflow.com/a/44203633/8538597
        soup = BeautifulSoup(results.content, "html.parser")

        for a in soup.find_all("a", class_="photoLink"):
            sleep(randint(1, 2))
            offer_url = "https:{}".format(a["href"])
            try:
                offer_result = requests.get(offer_url)
            except requests.exceptions.Timeout as e:
                # Maybe set up for a retry, or continue in a retry loop
                print("Connection Timeout: {}. Skipping to next offer.".format(e))
                offers_skipped = offers_skipped + 1
                continue
            except requests.exceptions.TooManyRedirects as e:
                # Tell the user their URL was bad and try a different one
                print("Too many redirects: {}. Skipping to next offer.".format(e))
                offers_skipped = offers_skipped + 1
                continue
            except requests.exceptions.RequestException as e:
                # catastrophic error. bail.
                raise SystemExit(e)

            soup = BeautifulSoup(offer_result.content, "html.parser")
            # Regex to remove all characters from string that are not numbers or decimal points/commas
            trim = re.compile(r"[^\d.,]+")

            # Get property price and price per square meter
            price_offer = (
                soup.find("span", id="cena").text
                if soup.find("span", id="cena")
                else np.nan
            )
            if price_offer is not np.nan:
                price_offer = trim.sub("", price_offer)
            price.append(price_offer)

            price_sqrm_offer = (
                soup.find("span", id="cenakv").text
                if soup.find("span", id="cenakv")
                else np.nan
            )
            if price_sqrm_offer is not np.nan:
                price_sqrm_offer = trim.sub("", price_sqrm_offer)
                price_sqrm_offer = price_sqrm_offer.rstrip(".")
            price_sqrm.append(price_sqrm_offer)

            # Get property data
            list_details = soup.find("ul", class_="imotData")
            split_details = list(list_details.stripped_strings)

            iter_details = iter(split_details)
            detail_pairs = [c + next(iter_details, "") for c in iter_details]

            # Iterate through pairs to extract information
            heating_bool = 0
            gas_bool = 0
            floor_num = np.nan
            year_built_result = np.nan
            construction_type_formatted = np.nan
            sqr_m_formatted = np.nan
            for detail in detail_pairs:
                if "Квадратура" in detail:
                    result = trim.sub("", detail)
                    sqr_m_formatted = result.rstrip(".")
                if "Етаж" in detail:
                    result = detail.split()[0]
                    if "Партер" in detail:
                        floor_num = 0
                    else:
                        # TODO: Fix this stupid code
                        result = result.lstrip("Етаж:")
                        result = result.rstrip("-ти")
                        result = result.rstrip("-ви")
                        result = result.rstrip("-ми")
                        floor_num = result.rstrip("-ри")
                if "Газ" in detail:
                    result = detail.lstrip("Газ:")
                    gas_bool = 1 if result == "ДА" else 0
                # Important! 'T' - in bulgarian, 'E' - in English
                if "ТEЦ" in detail:
                    result = detail.lstrip("ТEЦ:")
                    heating_bool = 1 if result == "ДА" else 0
                if "Строителство" in detail:
                    result = detail.split()
                    result_construction = result[0].lstrip("Строителство:")
                    construction_type_formatted = result_construction.rstrip(",")
                    year_built_result = result[1] if len(result) > 1 else np.nan
            heating.append(heating_bool)
            gas.append(gas_bool)
            floor.append(floor_num)
            year_built.append(year_built_result)
            construction_type.append(construction_type_formatted)
            sqr_m.append(sqr_m_formatted)
            # Fill in other information
            offer_furnished = 1 if soup.find("div", text="• Обзаведен") else 0
            furnished.append(offer_furnished)
            offer_security = 1 if soup.find("div", text="• Охрана") else 0
            security.append(offer_security)
            offer_entrance_control = (
                1 if soup.find("div", text="• Контрол на достъпа") else 0
            )
            entrance_control.append(offer_entrance_control)
            offer_passageway = 1 if soup.find("div", text="• С преход") else 0
            passageway.append(offer_passageway)

        url = url.rstrip("{}".format(current_page))
        current_page = current_page + 1
        url = url + str(current_page)
        sleep(randint(1, 2))
    try:
        offers = pd.DataFrame(
            {
                "apartment_type": apartment_type,
                "district": district,
                "price": price,
                "sqr_m": sqr_m,
                "price_sqrm": price_sqrm,
                "currency": "EUR",
                "year": year_built,
                "floor": floor,
                "gas": gas,
                "heating": heating,
                "construction_type": construction_type,
                "furnished": furnished,
                "entrance_control": entrance_control,
                "security": security,
                "passageway": passageway,
            }
        )
        print(offers)
        print(
            "Pages Skipped: {} ; Offers skipped: {}".format(
                pages_skipped, offers_skipped
            )
        )
        if len(offers) > 0:
            offers.to_csv("offers_partial.csv", mode="a", header=False)
            offers = offers.reset_index()
        return offers
    except ValueError as err:
        print(
            len(passageway),
            len(price),
            len(price_sqrm),
            len(year_built),
            len(floor),
            len(gas),
            len(heating),
            len(construction_type),
            len(furnished),
            len(entrance_control),
            len(security),
        )
        print("Something went wrong with the dataframe: {}".format(err))

