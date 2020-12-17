import mapping
import scraper

import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common import exceptions as exc
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# driver = webdriver.Chrome(
#     executable_path=r"C:\Users\IVAN PC\ChromeDriver\chromedriver.exe"
# )
driver = webdriver.Chrome(ChromeDriverManager().install())
timeout = 12
wait = WebDriverWait(driver, timeout)
districts = mapping.SOFIA_BG_EN_NEIGHBOURHOOD_MAPPING
apartment_types = mapping.SOFIA_APARTMENT_TYPES_MAPPING
offer_df_results = []
districts_skipped = []

def main():
    for apartment_name, apartment_code in apartment_types.items():
        for district_bg, district_en in districts.items():
            sleep(3)
            driver.get("https://www.imot.bg/pcgi/imot.cgi?act=2&rub=1")
            try:
                # Wait for page to load
                element_present = EC.presence_of_element_located((By.CLASS_NAME, "sw510"))
                wait.until(element_present)

                # Select region
                select = Select(driver.find_element_by_class_name("sw510"))
                select.select_by_value("град София")
                bedroom_select = "vi{}".format(apartment_code)

                # Select number of bedrooms
                element_present = EC.presence_of_element_located((By.ID, bedroom_select))
                wait.until(element_present)
                driver.find_element_by_id(bedroom_select).click()
                action = ActionChains(driver)

                # Select district
                parent_select = driver.find_element_by_xpath("//select[@name='ri']")
                element_select = parent_select.find_element_by_xpath(
                    "//option[@value='" + district_bg + "']"
                )
                action.double_click(element_select).perform()

                # Wait before going to results - ensures that filter is clicked
                driver.implicitly_wait(1000)
                
                # Go to search results
                search_button = driver.find_element_by_xpath("//input[@value='Т Ъ Р С И']")
                search_button.click()

                # Wait for page to load
                element_present = EC.presence_of_element_located(
                    (By.XPATH, "//span[@class='pageNumbersInfo']")
                )
                wait.until(element_present)

                # Assert that search filters have been applied
                check_filters_applied("град София", district_bg.upper())
                
                # Determine number of pages
                pages_element = driver.find_element_by_xpath(
                    "//span[@class='pageNumbersInfo']"
                )
                num_pages = determine_number_of_pages(pages_element)

                # Begin scraping process
                url = driver.current_url
                result = scraper.scrape_by_url(url, apartment_name, district_en, num_pages)
                offer_df_results.append(result)

            except exc.NoSuchElementException as ex:
                print("No such element: {}".format(ex))
                print("{} skipped due to no such element".format(district_en))
                districts_skipped.append(district_en)
                continue

            except exc.TimeoutException as ex:
                print("Timed out waiting for element to load: {}".format(ex))
                print("{} skipped due to timeout of element".format(district_en))
                districts_skipped.append(district_en)
                continue

    # Combine dataframes and save information to disk
    offers_list = pd.concat(offer_df_results)
    offers_list = offers_list.reset_index()
    offers_list.to_pickle("offers.pkl")
    offers_list.to_csv("offers.csv")
    driver.close()


def check_filters_applied(region, district):
    """
    On the results page, check if the filters have been applied.
    """
    filter_region = driver.find_elements_by_xpath(
        "//*[contains(text(),'" + region + "')]"
    )
    assert filter_region

    filter_district = driver.find_elements_by_xpath(
        "//*[contains(text(),'" + district + "')]"
    )
    assert filter_district


def determine_number_of_pages(pages_element):
    """
    Pass in page information, e.g. 'Страница 1 от 25'.
    Format it to get the second number which will be the total amount of pages.
    """
    pages_string = pages_element.text
    pages_raw = [int(s) for s in pages_string.split() if s.isdigit()]
    pages = pages_raw[1]
    return pages

main()
