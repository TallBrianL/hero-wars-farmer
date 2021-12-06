from hero_wars_farmer import HeroWarsFarmer

loot_desired = [
    ("pastorsSeal", 22),
    ("serenityStone", 14),
    ("lionArmor", 26),
    # ("scorchingQuiver", 6),
    # ("dragonHeart", 26),
    ("lute", 10),
    # ("sacredRosary", 15),
    # ("dragonShield", 15),
    # ("enchantedLute", 20),
    # ("magicHat", 25),
    # ("needle", 20),
    ("handOfGlory", 20),
    # ("astaroth", 9),
    ("flamingHeart", 66)
]

MAX_CHAPTER_TO_FARM = 8

if __name__ == '__main__':
    hwf = HeroWarsFarmer()

    cities_to_farm = hwf.select_cities(loot_desired, MAX_CHAPTER_TO_FARM)

    if cities_to_farm:
        hwf.enter_campaign()
        hwf.farm_cities(cities_to_farm)
    else:
        print("No cities to farm")
