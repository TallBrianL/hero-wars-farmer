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

    def move_and_click_offset(self, item, my_time):
        pos = item['position']
        offset_pos = (pos[0] + self.offset[0], pos[1] + self.offset[1])
        self.move_and_click(offset_pos, my_time)

    @staticmethod
    def move_and_click(loc, my_time):
        pyautogui.moveTo(*loc, duration=my_time)
        time.sleep(0.5)
        pyautogui.click(*loc)

    def get_current_chapter(self):
        pos = (302, 189)
        offset_pos = (pos[0] + self.offset[0], pos[1] + self.offset[1])
        span = (708, 222)
        return self.ocr_chapter(offset_pos, span)

    @staticmethod
    def ocr_chapter(pos, span):
        time.sleep(0.5)
        temp = pyautogui.screenshot()
        cropped = temp.crop((*pos, *span))
        my_string = pytesseract.image_to_string(cropped)
        words = my_string.split()
        assert(words[0] == "Chapter")
        return int(words[1][:-1])

    def enter_campaign(self):
        self.move_and_click_offset(self.controls["enterCampaign"], 1)
        self.current_chapter = self.get_current_chapter()

    def go_to_chapter(self, chapter):
        while chapter < self.current_chapter:
            self.move_and_click_offset(self.controls["chapter_down"], .2)
            time.sleep(0.5)
            self.current_chapter -= 1
        while chapter > self.current_chapter:
            self.move_and_click_offset(self.controls["chapter_up"], .2)
            time.sleep(0.5)
            self.current_chapter += 1

    def run_level(self, city, my_time=DEFAULT_TIME):
        self.go_to_chapter(city["chapter"])
        self.move_and_click_offset(city, .5)
        self.move_and_click_offset(self.controls["start"], .2)
        self.move_and_click_offset(self.controls["battle"], .2)
        self.move_and_click_offset(self.controls["auto"], 5.5)
        wait(my_time)
        self.move_and_click_offset(self.controls["cont"], 1)

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
                self.run_level(city)

    def run_tower(self):
        while True:
            self.run_tower_floor()

    def run_tower_floor(self):
        is_level_identified = False
        for _ in range(10):
            if pyautogui.locateCenterOnScreen('screenshots\\tower_to_battle.PNG'):
                print('battle detected')
                self.run_battle_floor()
                is_level_identified = True
            elif pyautogui.locateCenterOnScreen('screenshots\\tower_treasure.PNG'):
                self.run_treasure_floor()
                is_level_identified = True
            elif pyautogui.locateCenterOnScreen('screenshots\\tower_buff_chest.PNG'):
                self.run_buff_floor()
                is_level_identified = True
            elif pyautogui.locateCenterOnScreen('screenshots\\tower_buff_chest2.PNG'):
                self.run_buff_floor()
                is_level_identified = True
            elif pyautogui.locateCenterOnScreen('screenshots\\tower_treasure2.PNG'):
                self.run_treasure_floor()
                is_level_identified = True
        if is_level_identified:
            time.sleep(1)
            return 0
        else:
            raise ValueError("Could not find tower floor type")

    @staticmethod
    def push(button, max_iters=10):
        loc = None
        count = 0
        while not loc and count < max_iters:
            loc = pyautogui.locateCenterOnScreen('screenshots\\' + button + '.PNG')
            time.sleep(0.1)
            count += 1
        if not loc:
            raise RuntimeError("Could not find " + button + " button")
        HeroWarsFarmer.move_and_click(loc, 0.2)

    @staticmethod
    def run_battle_floor():
        HeroWarsFarmer.push('tower_to_battle')
        try:
            HeroWarsFarmer.push('tower_battle_skip')
        except RuntimeError:
            HeroWarsFarmer.push('tower_battle_attack')
        HeroWarsFarmer.push('to_battle')
        HeroWarsFarmer.push('auto_off', 100)
        t = 0
        while t < 180:
            if pyautogui.locateCenterOnScreen('screenshots\\victory.PNG'):
                print('Victory!')
                HeroWarsFarmer.push('ok')
                return 0
            elif pyautogui.locateCenterOnScreen('screenshots\\defeat.PNG'):
                print('Defeat :(')
                HeroWarsFarmer.push('ok')
                return 1
            time.sleep(0.5)
            t += 0.5
        raise RuntimeError("Battle End Not Detected, Timeout")

    def run_buff_floor(self):
        try:
            self.push('tower_buff_chest')
        except RuntimeError:
            self.push('tower_buff_chest2')
        self.move_and_click_offset(self.controls["tower_buff_close"], 0.2)
        try:
            HeroWarsFarmer.push('tower_proceed')
        except RuntimeError:
            HeroWarsFarmer.push('tower_proceed2')
        return 0

    @staticmethod
    def run_treasure_floor():
        try:
            HeroWarsFarmer.push('tower_treasure')
        except RuntimeError:
            HeroWarsFarmer.push('tower_treasure2')
        HeroWarsFarmer.push('tower_treasure_open')
        HeroWarsFarmer.push('proceed')
        return 0

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


if __name__ == '__main__':
    hwf = HeroWarsFarmer()
    hwf.run_tower()
