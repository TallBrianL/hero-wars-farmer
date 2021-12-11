import glob
import json
import time

import pyautogui
import pytesseract

DEFAULT_TIME = 110
DROP_RATE = .2


class HeroWarsFarmer:
    def __init__(self):
        self.current_chapter = None
        with open('coordinates.json') as coordinate_file:
            coordinates = json.load(coordinate_file)
            expected_logo_pos = (505, 121)
            logo_pos = pyautogui.locateCenterOnScreen('screenshots\\heroWarsTitleIcon.PNG')
            if not logo_pos:
                raise ValueError("Could not find Hero Wars logo, farmer NOT initialized")
            self.offset = (logo_pos[0] - expected_logo_pos[0], logo_pos[1] - expected_logo_pos[1])
            self.controls = list_to_dict(coordinates["general"])
            self.cities = list_to_dict(coordinates["cities"])

    def apply_offset(self, pos):
        return pos[0] + self.offset[0], pos[1] + self.offset[1]

    def click_item(self, item, my_time):
        pos = item['position']
        self.click_location(self.apply_offset(pos), my_time)

    @staticmethod
    def click_location(loc, my_time):
        pyautogui.moveTo(*loc, duration=my_time)
        time.sleep(0.5)
        pyautogui.click(*loc)

    @staticmethod
    def locate_file_any_suffix(needle, haystack):
        for f in glob.glob('screenshots\\' + needle + "*.PNG"):
            loc = pyautogui.locate(f, haystack)
            if loc:
                return pyautogui.center(loc)
        return None

    @staticmethod
    def locate_try_iters(image, max_iters=10):
        loc = None
        count = 0
        while not loc and count < max_iters:
            loc = pyautogui.locateCenterOnScreen('screenshots\\' + image + '.PNG')
            time.sleep(0.1)
            count += 1
        if not loc:
            raise RuntimeError("Could not find " + image)
        return loc

    @staticmethod
    def detect_and_push(button, max_iters=10):
        loc = HeroWarsFarmer.locate_try_iters(button, max_iters)
        HeroWarsFarmer.click_location(loc, 0.2)

    @staticmethod
    def ocr_screen(pos, span):
        time.sleep(0.5)
        temp = pyautogui.screenshot()
        cropped = temp.crop((*pos, *span))
        my_string = pytesseract.image_to_string(cropped)
        return my_string.split()

    # --------------------------------------------------
    # CAMPAIGN RUNNER
    def enter_campaign(self):
        self.click_item(self.controls["enterCampaign"], 1)
        self.current_chapter = self.get_current_chapter()

    def get_current_chapter(self):
        pos = (302, 189)
        span = (708, 222)
        my_string = self.ocr_screen(self.apply_offset(pos), span)
        words = my_string.split()
        assert (words[0] == "Chapter")
        return int(words[1][:-1])

    def go_to_chapter(self, chapter):
        while chapter < self.current_chapter:
            self.click_item(self.controls["chapter_down"], 0.2)
            time.sleep(0.5)
            self.current_chapter -= 1
        while chapter > self.current_chapter:
            self.click_item(self.controls["chapter_up"], 0.2)
            time.sleep(0.5)
            self.current_chapter += 1

    def run_campaign_level(self, city):
        self.go_to_chapter(city["chapter"])
        self.click_item(city, .5)
        self.click_item(self.controls["start"], 0.2)
        HeroWarsFarmer.detect_and_push('to_battle')
        HeroWarsFarmer.detect_and_push('auto_off', 100)
        HeroWarsFarmer.detect_battle_complete()

    def select_cities(self, loot_desired, max_level):
        cities = []
        for [loot, quantity] in loot_desired:
            cities_with_loot = [city for city in self.cities.values() if loot in city["loot"]]
            cities_within_maxlevel = [city for city in cities_with_loot if city["chapter"] <= max_level]
            try:
                highest_level_city = max(cities_within_maxlevel, key=lambda city: city["chapter"])
                cities.append((highest_level_city, round(quantity / DROP_RATE)))
            except ValueError:
                print("No cities with", loot, "found")
        print(cities)
        return cities

    def farm_cities(self, farm_list):
        for [city, quantity] in farm_list:
            for _ in range(quantity):
                self.run_campaign_level(city)

    # --------------------------------------------------
    # TOWER RUNNER
    def run_tower(self):
        print('running tower')
        while True:
            self.run_tower_floor()
            print('sleeping for 2')
            time.sleep(2)

    def run_tower_floor(self):
        print('detecting floor')
        count = 0
        loc = None

        while count < 10:
            print('detecting...')
            floor_screen_capture = pyautogui.screenshot()

            loc = self.locate_file_any_suffix('tower_to_battle', floor_screen_capture)
            if loc:
                print('battle detected')
                self.run_battle_floor(loc)
                break

            loc = self.locate_file_any_suffix('tower_treasure', floor_screen_capture)
            if loc:
                print('treasure detected')
                self.run_treasure_floor(loc)
                break

            loc = self.locate_file_any_suffix('tower_buff', floor_screen_capture)
            if loc:
                print('buff chest detected')
                self.run_buff_floor(loc)
                break

            count += 1

        if loc:
            return 0
        else:
            raise ValueError("Could not find tower floor type")

    @staticmethod
    def run_battle_floor(loc=None):
        print('running battle floor')
        if loc:
            HeroWarsFarmer.click_location(loc, 0.2)
        else:
            HeroWarsFarmer.detect_and_push('tower_to_battle')
        try:
            HeroWarsFarmer.detect_and_push('tower_battle_skip')
            return 0
        except RuntimeError:
            print('could not skip')
        HeroWarsFarmer.detect_and_push('tower_battle_attack')
        HeroWarsFarmer.detect_and_push('to_battle')
        HeroWarsFarmer.detect_and_push('auto_off', 100)
        HeroWarsFarmer.detect_battle_complete()

    @staticmethod
    def detect_battle_complete():
        t = 0
        while t < 180:
            floor_screen_capture = pyautogui.screenshot()
            loc = HeroWarsFarmer.locate_file_any_suffix('victory', floor_screen_capture)
            if loc:
                print('Victory!')
                HeroWarsFarmer.detect_and_push('continue')
                return 0
            loc = HeroWarsFarmer.locate_file_any_suffix('defeat', floor_screen_capture)
            if loc:
                print('Defeat :(')
                HeroWarsFarmer.detect_and_push('continue')
                return 1

            time.sleep(0.5)
            t += 0.5
            print('.', end='')
        raise RuntimeError("Battle End Not Detected, Timeout")

    def run_buff_floor(self, loc=None):
        print('running buff floor')
        if loc:
            HeroWarsFarmer.click_location(loc, 0.2)
        else:
            try:
                self.detect_and_push('tower_buff_chest')
            except RuntimeError:
                self.detect_and_push('tower_buff_chest2')
        self.click_item(self.controls["tower_buff_close"], 0.2)
        try:
            HeroWarsFarmer.detect_and_push('tower_proceed')
        except RuntimeError:
            HeroWarsFarmer.detect_and_push('tower_proceed2')
        return 0

    @staticmethod
    def run_treasure_floor(loc=None):
        print('running treasure floor')
        if loc:
            HeroWarsFarmer.click_location(loc, 0.2)
        else:
            try:
                HeroWarsFarmer.detect_and_push('tower_treasure')
            except RuntimeError:
                HeroWarsFarmer.detect_and_push('tower_treasure2')
        HeroWarsFarmer.detect_and_push('tower_treasure_open')
        HeroWarsFarmer.detect_and_push('proceed')
        return 0


def list_to_dict(item_list: list):
    named_dict = {}
    for value in item_list:
        named_dict[value["name"]] = value
    return named_dict


if __name__ == '__main__':
    hwf = HeroWarsFarmer()
    hwf.run_tower()
