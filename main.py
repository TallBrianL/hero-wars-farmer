from hero_wars_farmer import HeroWarsFarmer

MAX_CHAPTER_TO_FARM = 8

if __name__ == '__main__':
    hwf = HeroWarsFarmer()

    cities_to_farm = hwf.select_cities(MAX_CHAPTER_TO_FARM)

    if cities_to_farm:
        hwf.enter_campaign()
        hwf.farm_cities(cities_to_farm)
    else:
        print("No cities to farm")
