from hero_wars_farmer import HeroWarsFarmer

loot_desired = [
    ("lionArmor", 200),
    ("astaroth", 9)
]

MAX_CHAPTER_TO_FARM = 7
MAX_CHAPTER_AVAILABLE = 9

if __name__ == '__main__':
    hwf = HeroWarsFarmer(MAX_CHAPTER_AVAILABLE)

    cities_to_farm = hwf.select_cities(loot_desired, MAX_CHAPTER_TO_FARM)

    if cities_to_farm:
        hwf.enter_campaign()
        hwf.farm_cities(cities_to_farm)
    else:
        print("No cities to farm")
