import random

#Define the races, their rarity percentages, attributes, and passive abilities
races = {
    "Haseldan": {
        "rarity": 19.00,
        "attributes": ["+2 Fortitude", "+2 Strength"],
        "passive": "Receiving damage after reaching 20% health increases damage and defense by 2x for 40 seconds, indicated by a red tint. 2 minute cooldown." 'Achieving Ultraclass - Bloodline - Restore 40 health and gain a 2x attack and defense buff for 30 seconds. After, the Haseldan will be knocked for 5 seconds. 10 minute cooldown.'
    },
    "Rigan": {
        "rarity": 16.2,
        "attributes": ["+2 Intelligence", "+2 Charisma"],
        "passive": "Mana Affinity - Rigans get 2x mana charge. This allows them to flee and chase extremely effectively, and makes them fearsome mages." 'Ice Affinity - Deals 1.25x more damage with Ice spells' 'Achieving Ultraclass: Flood - an ability which grants you unlimited mana for ~30 seconds. However after use, this caps the users mana at 50% for ~15 seconds. It also has a 10 minute cooldown. (Voiding/rejoining also resets the cooldown.)'
    },
    "Ashiin": {
        "rarity": 14.30,
        "attributes": ["+2 strength", "+2 Fortitude"],
        "passive": "Trained Combat: Changes the animation of your M1 combo. Your fist damage is increased by 2x." "Agility - Temporarily increase movement and attack speed. You need a dagger equipped to use this. The end of the buff is signaled with a blue flash on your character. 30 second cooldown."
    },
    "Castellan": {
        "rarity": 13.30,
        "attributes": ["+2 Intelligence", "+2 Wisdom"],
        "passive": "Swift Mana - Castellans have a x1.25 faster mana charge." "Wise Casting - Castellans get 1.2x Scholar's Boon." "Snap Excellence - They are able to get 2 snap spells without dealing with the Soul Master. Also gains snap exp MUCH quicker and wont have to cast ignis a gazillion times in a row. Castellans lose 40% less HP per soul snap, example if you have 100 HP, one soul snap will put you to 97 as a castellan instead of the default 95."
    },
    "Kasparan": {
        "rarity": 8.6,
        "attributes": ["+2 Strength", "+2 Fortitude"],
        "passive": "+1 life to the party" "Draconic Flame - Kasparans deal 1.25x more damage with fire spells." "Dragonborn - Kasparans spawn with Dragon Speech." "Achieving Ultraclass: Respirare - Charging mana and using this will make you breathe fire. " "Achieving Ultraclass: Dragon Scales - Slash damage does 25% less damage and 50% less damage from fire."
    },
    "Gaian": {
        "rarity": 7.6,
        "attributes": ["+2 Fortitude", "+2 strength"],
        "passive": "Overheat - Having high temperature causes a Gaian's arms to have a sparking effect. Punches will increase temperature and will have +1 damage." "Repair - Enter a crouching animation and progressively recover health. Repairing speed increases upon reaching super class, then again upon reaching ultra class. The recovery is a specific % of your max HP per second." "Oil Blood - Gaians have oil for blood. They cannot be poisoned, and cannot become vampires. Vampires cannot (successfully) feed on Gaians. They can try but it won't do anything." "Robot Anatomy - Gaians are more resistant to broken bone injuries, cannot get scars, and immune to injuries that affect vision." "Iron Body - Sharp attacks do not deal chip damage while blocking" "Slash Resistance - Slash damage does 25% less damage." "Robot Mind - Gaians are immune to Insanity and Concussions. Dominus and the Master Illusionist quest bypass this racial ability." "Gaian Armor - Gaians have special armor that can be upgraded twice. Tier 1 Gaian Armor 1.15x Health Cannot regenerate health Obtained on spawn"
    },
    "Navaran": {
        "rarity": 3.8,
        "attributes": ["+2 charisma", "+2 Agility"],
        "passive": "Emulate - Copy a single ability from someone else. Only one skill can be emulated and it can be changed" "Devour - When executing a knocked entity, they will use different animation and devour their prey. This restores hunger." "Achieving your Ultra class - You are now able to emulate Ultra skills using Emulate"
    },
    "Madrasian": {
        "rarity": 6.80,
        "attributes": ["+2 Fortitude", "+2 Willpower", ],
        "passive": "Shift - Change your appearance to the targeted person" "Observe Resist - Hide yourself from Illusionists" "Trinket Shift - Obtained upon reaching Ultraclass. Shift into a random trinket or artifact."
    },
    "Dinakeri": {
        "rarity": 1.9,
        "attributes": ["+2 Intelligence", "+2 Willpower"],
        "passive": "Soul Rip: Rip the soul of a knocked player, executing them and granting the Dinakeri a rune." "Berserk Mode: Soul Rip M2 with an available rune consumes it, the following modifiers then apply for 25 seconds:" "Rune Casting: Casting a spell with no mana charged consumes a rune which makes the spell perfectly cast with the required mana."
    },
    "Morvid": {
        "rarity": 1.9,
        "attributes": ["+2 Intelligence", "+2 Fortitude"],
        "passive": "Feather Falling - Fall damage is reduced by a set amount. Unable to die from fall damage." "Mana Lineage - Spawns with Mana." "Cannibalism - Gripping other Morvids causes you to eat them, restoring hunger and helping you unlock your forms." "Soul Rebound - After the move flock ends, Hoppa M2 is put on a cooldown for 2 seconds; Hoppa M1 gains 4 additional hand signs for 1 second (making it 8 instead of 4)." "Phase 1 - Starting phase for morvids, all of the regular abilites." "Phase 2 - Nothing changes except the option to use hair." "Phase 3 - Gained at 20 Morvid grips - Morvids lose their beaks and unlock an ability called Flock" "Flock makes you invincible and invisible for around 2 seconds. " "Has a cooldown of around 20 seconds." "Flock can be used with mana run." "Alternatively, flock increases your base speed."
    },
    "Fischeran": {
        "rarity": 1.00,
        "attributes": ["+2 Intelligence, , ""+2 Agility"] ,
        "passive": "Wind Shield - Phase through 4 attacks with reduced stun. 5th hit has reduced stun but damage is still provided. Wind Shield starts its cooldown after one shield is consumed." "Sky's Sailors - 1.1875x damage with all wind spells" "Sky's Temperature - Punching a Fischeran with Wind Shield active will lower your temperature." "Skybound - Fischerans are able to go to Castle in the Sky with one gem." "Mana Lineage - Spawn with Mana."  "no longer become a Vampire" "Dissolve - This ability is obtained upon reaching your Ultra class. Turn into a puddle of water for 20 seconds. The Fischeran is immune to all damage sources, but is unable to regenerate health, use abilities, or charge mana."
    },
    # Newly added races with same stats and rarity as Lightborn
    "Vind": {
        "rarity": 1.00,
        "attributes": ["+2 Intelligence ", "+2 Fortitude"],
        "passive": "Tempest Soul - Using Tempest Soul will activate a barrier that reflects spells and increases speed for its duration. Tempest Soul can be activated with any percentage of Mana, except 0%, You can use Mana Shield by holding F with Tempest Soul and mana charged. Tempest Soul has a 10 second cooldown that starts after the effect ends." "Faster Regeneration - 1.1x health regeneration.(It multiplies with you current regen so if you have 1.3x regen it becomes 1.4x regen)" "Skybound -Vinds can go to Castle In the Sky via Ezlo with only one gem." "Calm Mind - Vinds are unable to get grippo mode from gripping." "Ideal Sailors - Vinds cannot get scars on their face." "Unnatural Blood - Vinds have unnatural wind-elemental blood; cannot become Vampires." "Mana Lineage - Vinds spawn with Mana." "Sky's Sailors - 1.1875x damage with all wind spells (Nerfed from 1.5x to 1.25, then 1.1875x on June 9, 2022)" "Gaia - Getting your Ultra Class makes Tempest Soul last 4 seconds."
    },
    "Dzin": {
        "rarity": 1.00,
        "attributes": ["+2 strength " "+2 Agility"],
        "passive": "Unbreakable - Immunity to all mind spells and traumas. Dominus and the Master Illusionist quest bypass this racial ability." "World's Pulse - (Toggleable) Highlights players and NPCs with a light blue aura which can be seen through walls" "Achieving Ultraclass - Awakened - (Active) Allows the user to automatically dodge attacks that they've been hit with, negating damage and stun. makes them open their third eye." "More session = More dodges" 
    },
    "Azael": {
        "rarity": 0.010,
        "attributes": ["+5 To Any Stat", "+2 Intelligence"],
        "passive": " Hell's Flame - Cannot have the normal orange fire, Sealed Sword white fire, or Vanguard azure fire status effects applied to them by any means other than backfiring their own spells. Azaels are also immune to most fire attacks. Azaels cannot be hit or stunned at ALL by the following fire attacks:" "Par's Curse - Capped to 2 lives and can't go Vampire, having extra lives upon becoming an Azael will not reduce the current amount of lives" "Faster Mana Charge - Your mana charges at a 1.5x faster rate." 
    },
    "Construct": {
        "rarity": 0.010,
        "attributes": ["+5 To Any Stat", "+2 Fortitude"],
        "passive": "Winterborn - Passive 3.75 cold resistance." "Galvanize - Restore 50% Health in exchange for 49% toxicity. This has a windup and a Construct can be instantly executed or injured by Nocere before healing. Obtained after ingesting 50+ potions. 10 minute cooldown. " "Enhanced Toxicity Bar - Construct have a 7x toxicity bar, being able to drink 7x the amount of potions a regular person could." "Artificial Blood - Construct have unnatural green blood. This blood is shared only with Scrooms, however Constructs can be fed on by Vampires. " "Mercenary Drink - Construct can walk and roll around while drinking potions."   },
    
    
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