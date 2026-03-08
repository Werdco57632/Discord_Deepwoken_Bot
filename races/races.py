import random


#Define the races, their rarity percentages, attributes, and passive abilities
races = {
    "Adret": {
        "rarity": 20.50,
        "attributes": ["+2 Charisma", "+2 Willpower"],
        "passive": "Increased Starting Rep with Actions and Passive Autodidact (stacks with Autodidact Boon)"
    },
    "Celtor": {
        "rarity": 20.50,
        "attributes": ["+2 Intelligence", "+2 Charisma"],
        "passive": "Cheaper Ships, 10% Health Increase on Ships"
    },
    "Etrean": {
        "rarity": 20.50,
        "attributes": ["+2 Agility", "+2 Intelligence", "+1 Health"],
        "passive": "Reduce Status Effects Time, Reduced Damage from Acid Rain"
    },
    "Canor": {
        "rarity": 15.90,
        "attributes": ["+2 Strength", "+2 Charisma"],
        "passive": "Reduces Team Damage"
    },
    "Gremor": {
        "rarity": 13.60,
        "attributes": ["+2 Strength", "+2 Fortitude"],
        "passive": "Lose Less Hunger and Gain Compass"
    },
    "Felinor": {
        "rarity": 9.10,
        "attributes": ["+2 Agility", "+2 Charisma"],
        "passive": "Increased Stealth and Improved Parkour on Wooden Surfaces"
    },
    "Khan": {
        "rarity": 9.10,
        "attributes": ["+2 Strength", "+2 Agility"],
        "passive": "Items can be Equipped with less Statpoints"
    },
    "Vesperian": {
        "rarity": 6.80,
        "attributes": ["+2 Fortitude", "+2 Willpower", "+2 Health"],
        "passive": "Additional Armor"
    },
    "Capra": {
        "rarity": 2.30,
        "attributes": ["+2 Intelligence", "+2 Willpower"],
        "passive": "Increased Food Gain from Eating, or Improves Rest to Group, or Improves Sanity"
    },
    "Ganymede": {
        "rarity": 2.30,
        "attributes": ["+2 Intelligence", "+2 Willpower"],
        "passive": "Resistance from Sanity"
    },
    "Lightborn": {
        "rarity": 0.010,
        "attributes": ["+5 To Any Stat", "+2 Agility", "+2 Intelligence"],
        "passive": "Reduced Damage from Acid Rain"
    },
    # Newly added races with same stats and rarity as Lightborn
    "Heliodar": {
        "rarity": 0.010,
        "attributes": ["+3 Strength", "+3 Fortitude", "+2 Agility", "+2 Intelligence"],
        "passive": "Gives the user the ability to temporarily fly, sprouting glowing orange wings, though this is temporary and lasts about 15 seconds. This aspect is also not immune to fall damage and can still die from it."
    },
    "Drakkard": {
        "rarity": 0.010,
        "attributes": ["+2 Agility", "+2 Fortitude", ],
        "passive": "Allows you to meditate, emitting a white aura and causing two white orbs to circle your head." "Very heavily reduces your hunger and thirst consumption." 'You passively gain EXP and Attribute EXP.' "You regenerate health at a mediocre rate, which is slightly reduced when in combat."
    },
    "Auroran": {
        "rarity": 0.010,
        "attributes": ["+3 Fortitude", "+2 Strength", ],
        "passive": "Gain a compass at the top of your screen that points South." "Reduced hunger loss" "If blind, gain a slight range of clear vision around you"
    },
    "Aberrant Capra": {
        "rarity": 0.010,
        "attributes": ["+2 Intelligence", "2 Willpower"],
        "passive": "Buffs the sanity of one person they choose around them as long as they are at a campfire or level 5+"
    },
    "Primal Vesperian": {
        "rarity": 0.010,
        "attributes": ["+2 Fortitude", "+2 Willpower"],
        "passive": "5% damage reduction. Degrades with damage but can be replenished at a campfire" 'This buff also stacks with Exoskeleton ( Rare Talent ) albeit is slightly reduced.'
    }
}

#Create a list of races based on their rarity percentages
weighted_races = []
for race, data in races.items():
    weighted_races.extend([race] * int(data["rarity"]))

#Randomly select a race
selected_race = random.choice(weighted_races)
race_data = races[selected_race]

#Display the selected race and its details
print(f"Selected Race: {selected_race}")
print("Attributes:")
for attribute in race_data["attributes"]:
    print(f"  - {attribute}")
print(f"Passive Ability: {race_data['passive']}")