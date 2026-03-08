import os
import json
import re



directory = os.path.dirname(os.path.abspath(__file__))

# Open file and read lines
with open(directory+'\\talents_raw.txt', 'r') as file:
    text_array = file.readlines()

# Set variable defaults
json_data = {"_": {}}
talents_list = []
name = "_"
i = 0

# Iterate over every line in the text file
for i in range(i, len(text_array)):
    # Check for word after first open bracket ("[")
    match = re.search(r'\[([^\[\]\s]+)', text_array[i])
    if match:
        bracket_index = text_array[i].find('[')
        name = text_array[i][:bracket_index].strip()
        talents_list.append(str(name))

i = 0



# Define function to check prerequisites
def prerequisites(prefix):
    global name
    weapons = ["Dagger", "a spear", "Fists", "Rapier", "a Shield.", "Heavy", "a Greatsword", "a Greathammer"]
    if text_array[i].startswith(prefix) and json_data[name]['prerequisites'] == {}:
        items = text_array[i][len(prefix):].split(',')
        items = [item.strip() for item in items]

        n = 0
        json_data[name]['requires'] = []
        while n < len(items):
            parts = items[n].split(maxsplit=1)
            if parts and parts[0].isdigit():
                number = int(parts[0])
                key = parts[1] if len(parts) > 1 else ""
                json_data[name]['prerequisites'][key] = number
                items.pop(n)
            elif (parts[0] == "Power" and parts[1].isdigit()):
                json_data[name]['prerequisites']['Power'] = int(parts[1])
                items.pop(n)
            elif (parts[0] == "Using" and parts[1] in weapons):
                if (parts[1] == "a spear"):
                    json_data[name]['weapon'] = "Spear"
                else:
                    json_data[name]['weapon'] = parts[1]
                items.pop(n)
            elif (parts[0] == "Use" and parts[1] in weapons):
                if (parts[1] == "a Shield."):
                    json_data[name]['weapon'] = "Shield"
                elif (parts[1] == "a Greatsword"):
                    json_data[name]['weapon'] = "Greatsword"
                elif (parts[1] == "a Greathammer"):
                    json_data[name]['weapon'] = "Greathammer"
                else:
                    json_data[name]['weapon'] = parts[1]
                items.pop(n)
            elif (parts[0] == "Dagger"):
                json_data[name]['weapon'] = "Dagger"
                items.pop(n)
            elif (parts[0] == "Fists"):
                json_data[name]['weapon'] = "Fists"
                items.pop(n)
            elif (parts[0] == "Heavy"):
                json_data[name]['weapon'] = "Heavy Weapon"
                items.pop(n)
            elif (parts[0] == "All" or parts[0] == "all"):
                if parts[1] == "Alley Cat Talents":
                    json_data[name]['requires'] += ["Endurance Runner","Scaredy Cat"]
                elif parts[1] == "common Bastion Talents":
                    json_data[name]['requires'] += ["Battle Tendency","Braced Collapse","Moving Fortress","Perseverance"]
                elif parts[1] == "Butterfly Talents":
                    json_data[name]['requires'] += ["Swift Rebound","Evasive Expert","Risky Moves"]
                elif parts[1] == "Charm Caster Talents":
                    json_data[name]['requires'] += ["Charismatic Cast","Chaotic Charm","Lasting Charisma","Tough Love"]
                elif parts[1] == "Assassin Talents":
                    json_data[name]['requires'] += ["Deep Wound","Lights Out","Lowstride","Unseen Threat"]
                elif parts[1] == "Silvertongue Talents":
                    json_data[name]['requires'] += ["Friends in High Places","Golden Tongue","Snake Oil"]
                elif parts[1] == "Thief Talents":
                    json_data[name]['requires'] += ["Cap Artist","Cap Artist","Pickpocket","Master Thief"]
                items.pop(n)
            elif (parts[0] == "None"):
                items.pop(n)
            else:
                n += 1


        skills = ["Power","Strength","Fortitude","Agility","Intelligence","Willpower","Charisma","Medium Weapon","Light Weapon","Heavy Weapon"]
        if (any(key not in skills for key in json_data[name]['prerequisites'])):
            del json_data[name]
            name = "_"
        else:
            json_data[name]['requires'] = json_data[name]['requires']+[x for x in items if x in talents_list]
            for x in items:
                if x not in talents_list:
                    print(f"prerequisite {name} | {x}")
                    del json_data[name]
                    name = "_"
                    break

        return True
        



# Get talent name and rarity
ignoremode = False
for i in range(i, len(text_array)):
    json_data["_"] = {}

    # Check for new talent ("[")
    match = re.search(r'\[([^\[\]\s]+)', text_array[i])
    if match:
        # Exclude spesific talents
        bad_names = ["Blinded", "Ardour Scream", "Water off a Duck's Back", "Chain of Perfection"]
        
        # Get the talent name
        bracket_index = text_array[i].find('[')
        name = text_array[i][:bracket_index].strip()

        # Get the description
        desc_match = re.search(r'\]\s*-\s*(.+)', text_array[i])

        # Get the exclusive category
        #match_ex = re.search(r'\[[^,\]]*,\s*([^\s\]]+)', text_array[i])

        # Check if valid category and not a magic talent
        categories = ["Common", "Rare", "Advanced", "Legendary"]
        #bad_ex_categories = ["Flamecharm","Frostdraw","Thundercall","Galebreathe","Shadowcast","Ironsing","Bloodrend", "Equipment"]

        # Check for bad exclusive category
        bad_category = False
        if re.search(r'\[[^\]]*Exclusive[^\]]*\]', text_array[i]) and not (re.search(r'\[[^\]]*Rapier Exclusive[^\]]*\]', text_array[i]) or re.search(r'\[[^\]]*Charisma Exclusive[^\]]*\]', text_array[i]) or re.search(r'\[[^\]]*Agility Exclusive[^\]]*\]', text_array[i])):
                bad_category = True

        if (match.group(1) not in categories) or bad_category or (name in bad_names):
            #print(f"category {name} | [{match.group(1)}]")
            ignoremode = True
            name = "_"
            continue
        else:
            ignoremode = False

            json_data[name] = {}
            json_data[name]['category'] = match.group(1)
            json_data[name]['description'] = desc_match.group(1).strip() if desc_match else ""
            json_data[name]['prerequisites'] = {}
            json_data[name]['requires'] = []
            json_data[name]['exclusive'] = []
            json_data[name]['weapon'] = ""
            continue
    if not ignoremode:
        if text_array[i].startswith("Obtained"):
            del json_data[name]
            name = "_"
            continue
        if prerequisites("Prerequisites: "): continue
        if prerequisites("Prerequisite: "): continue
        if prerequisites("Prerequisities: "): continue
        if prerequisites("Confirmed Prerequisites"): continue

        prefix = "Mutual Exclusive: "
        if text_array[i].startswith(prefix):
            items = text_array[i][len(prefix):].split(',')
            items = [item.strip() for item in items]
            for x in items:
                if x not in talents_list:
                    print(f"exclusive {name} | {x}")
            json_data[name]['exclusive'] = [x for x in items if x in talents_list]
            continue


del json_data["_"]

with open(directory+'\\talents.json', 'w') as file:
    json.dump(json_data, file, indent=4) # Indent = 4 to make it look nice :)
    
with open(directory+'\\talents_list.txt', 'w') as file:
    file.write('\n'.join(talents_list))


print("DONE")