from hero_wars_farmer import HeroWarsFarmer

loot_desired = {
    ("needle", 100)
}

MAX_CHAPTER = 5

if __name__ == '__main__':
    current_chapter = 9
    hwf = HeroWarsFarmer(current_chapter)

    cities_to_farm = hwf.select_cities(loot_desired, MAX_CHAPTER)

    if cities_to_farm:
        hwf.enter_campaign()
        hwf.farm_cities(cities_to_farm)
    else:
        print("No cities to farm")
