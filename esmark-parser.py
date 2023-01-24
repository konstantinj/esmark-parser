#!/usr/bin/env python3
import argparse
import sys
import time

import bs4 as bs
from selenium.common.exceptions import InvalidArgumentException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


class House:
    date: str = ''
    link: str = ''
    img: str = ''
    title: str = ''
    construction_year: str = ''
    floor_space: str = ''
    address: str = ''
    stars: str = ''
    facilities: list = []
    whirlpool: bool = False
    outside_whirlpool: bool = False
    sauna: bool = False
    beach_distance: int = 0
    shopping_distance: int = 0
    bedroom_count: int = 0
    people_count: int = 0
    price7: str = ''
    transaction_fee: str = ''
    power_fee: str = ''
    water_fee: str = ''
    endcleaning_fee: str = ''
    fireplace: bool = False
    barbecue: bool = False
    sandbox: bool = False
    swing: bool = False
    trampoline: bool = False
    internet: bool = False

    def to_csv(self, s: str):
        return f'"{self.link}"{s}' \
               f'"{self.date}"{s}' \
               f'=IMAGE("{self.img}"){s}' \
               f'"{self.stars}"{s}' \
               f'"{self.construction_year}"{s}' \
               f'"{self.sauna}"{s}' \
               f'"{self.outside_whirlpool}"{s}' \
               f'"{self.whirlpool}"{s}' \
               f'"{self.fireplace}"{s}' \
               f'"{self.barbecue}"{s}' \
               f'"{self.internet}"{s}' \
               f'"{self.trampoline}"{s}' \
               f'"{self.swing}"{s}' \
               f'"{self.sandbox}"{s}' \
               f'"{self.price7}"{s}' \
               f'"{self.transaction_fee}"{s}' \
               f'"{self.power_fee}"{s}' \
               f'"{self.water_fee}"{s}' \
               f'"{self.endcleaning_fee}"{s}' \
               f'"{self.floor_space}"{s}' \
               f'"{self.bedroom_count}"{s}' \
               f'"{self.people_count}"{s}' \
               f'"{self.beach_distance}"{s}' \
               f'"{self.shopping_distance}"{s}' \
               f'"{self.title}"{s}' \
               f'"{self.address}"'


def main(url: str, year: str, week: str, separator: str):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    element = driver.find_element(By.CSS_SELECTOR, 'a[data-goto="#tab-interior"]')
    # from https://stackoverflow.com/questions/52400233/error-other-element-would-receive-the-click-in-python
    # cookie banner seems to block the click
    driver.execute_script("arguments[0].click();", element)

    select = Select(driver.find_element(By.ID, 'DateSelector'))
    visible_text = [option.text for option in select.options if f'{year} (Woche {week})' in option.text][0]

    if "Belegt" not in visible_text:
        select.select_by_visible_text(visible_text)

    page = driver.page_source
    soup = bs.BeautifulSoup(page, 'lxml')

    interior = soup.select_one('div#singleInterior').text

    house = House()

    house.fireplace = interior.__contains__('Kaminofen')
    house.barbecue = interior.__contains__('Grill')
    house.sandbox = interior.__contains__('Sandkasten') or interior.__contains__('Sandkiste')
    house.swing = interior.__contains__('Schaukel')
    house.trampoline = interior.__contains__('Trampolin')
    house.internet = interior.__contains__('internet')

    house.date = visible_text
    house.link = url.strip()
    house.title = soup.find('h1', itemprop="name").text
    house.img = soup.find('img', id="mainLodgingImg").attrs['src']
    house.construction_year = soup.select_one('span:-soup-contains("Baujahr:")').next_sibling.text
    house.floor_space = soup.select_one('span:-soup-contains("Grundfläche:")').next_sibling.text
    house.bedroom_count = soup.select_one('span:-soup-contains("Schlafzimmer:")').next_sibling.text
    house.people_count = soup.find('div', {"class": "esFacility_156"}) \
        .find('span', {"class": "bText"}).text.replace(" pers.", "")
    house.beach_distance = soup.find('div', {"class": "esFacility_179"}) \
        .find('span', {"class": "bText"}).text.replace("\n", "").replace("m.", "")
    house.shopping_distance = soup.find('div', {"class": "esFacility_180"}) \
        .find('span', {"class": "bText"}).text.replace("\n", "").replace("m.", "")
    house.address = soup.find('h2').find('span').text
    house.stars = soup.find('div', {"class": "stars"}).find('span', {"class": "ratingValue"}).text
    items = soup.select('div[itemprop="additionalProperty"].facility')
    house.facilities = [item.attrs['class'][1] for item in items]  # remove facility class

    house.outside_whirlpool = house.facilities.__contains__('esFacility_292')
    house.whirlpool = house.facilities.__contains__('esFacility_289')
    house.sauna = house.facilities.__contains__('esFacility_133') or house.facilities.__contains__('esFacility_312')

    house.price7 = soup.find('b', id="select7Price").text
    house.transaction_fee = soup.find('div', {"class": "transaction_fee"}) \
        .find('div', {"class": "single-item-price-price"}).text
    house.power_fee = soup.find('div', {"class": "power"}) \
        .find('div', {"class": "single-item-price-price"}).text
    house.water_fee = soup.find('div', {"class": "water"}) \
        .find('div', {"class": "single-item-price-price"}).text
    house.endcleaning_fee = soup.find('div', {"class": "endcleaning"}) \
        .find('div', {"class": "single-item-price-price"}).text

    print(house.to_csv(separator))


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--year", help="put the year in 2 digit notation eg 23")
    parser.add_argument("--week", help="put the week number eg 16")
    parser.add_argument("--separator", help="separator eg ;")

    args = parser.parse_args()
    for url in sys.stdin:
        if 'Exit' == url.rstrip():
            break
        try:
            main(url, args.year, args.week, args.separator)
        except InvalidArgumentException:
            try:
                main(url, args.year, args.week, args.separator)
            except InvalidArgumentException:
                try:
                    main(url, args.year, args.week, args.separator)
                except InvalidArgumentException as e:
                    eprint(f'skipping {url} because of InvalidArgumentException {e}')
                    continue
