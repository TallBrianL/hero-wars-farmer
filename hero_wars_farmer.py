import json
import time

import pyautogui


class HeroWarsFarmer:
    def __init__(self, current_chapter=1):
        self.current_chapter = current_chapter
        with open('coordinates.json') as coordinate_file:
            coordinates = json.load(coordinate_file)
            self.controls = list_to_dict(coordinates["general"])
            self.cities = list_to_dict(coordinates["cities"])

    @staticmethod
    def move_and_click(item, my_time):
        pyautogui.moveTo(*item['position'], duration=my_time)
        time.sleep(0.5)
        pyautogui.click(*item['position'])

    def enter_campaign(self):
        self.move_and_click(self.controls["enterCampaign"], 1)

    def go_to_chapter(self, chapter):
        while chapter < self.current_chapter:
            self.move_and_click(self.controls["chapter_down"], .2)
            time.sleep(0.5)
            self.current_chapter -= 1
        while chapter > self.current_chapter:
            self.move_and_click(self.controls["chapter_up"], .2)
            time.sleep(0.5)
            self.current_chapter += 1

    def run_level(self, city, my_time=70):
        self.go_to_chapter(city["chapter"])
        self.move_and_click(city, .5)
        self.move_and_click(self.controls["start"], .2)
        self.move_and_click(self.controls["battle"], .2)
        self.move_and_click(self.controls["auto"], 5.5)
        wait(my_time)
        self.move_and_click(self.controls["cont"], 1)

    def select_cities(self, loot_desired, max_level):
        cities = []
        for [loot, quantity] in loot_desired:
            cities_with_loot = [city for city in self.cities.values() if loot in city["loot"]]
            cities_within_maxlevel = [city for city in cities_with_loot if city["chapter"] <= max_level]
            try:
                highest_level_city = max(cities_within_maxlevel, key=lambda city: city["chapter"])
                cities.append((highest_level_city, quantity))
            except ValueError:
                print("No cities with", loot, "found")
        return cities

    def farm_cities(self, farm_list):
        for [city, quantity] in farm_list:
            for _ in range(quantity):
                self.run_level(city)


def list_to_dict(item_list: list):
    named_dict = {}
    for value in item_list:
        named_dict[value["name"]] = value
    return named_dict


def wait(my_time):
    print('00', end='')
    for _ in range(my_time):
        time.sleep(1)
        print('.', end='')
        if not (_ + 1) % 10:
            for _2 in range(12):
                print('\b', end='')
            print(_ + 1, end='')
