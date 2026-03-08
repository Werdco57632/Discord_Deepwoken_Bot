import discord
from discord import app_commands
from discord.ext import commands
import random
import os
import json
import copy
import asyncio

ownername = "" # User to ping when error occurs
server_id = 0 # put server ID here for faster sync
bot_token = "" # put bot token here (keep this secret!)



#region -------------------------------- import/export json --------------------------------



# Get the full path to the json files
filename = os.path.dirname(os.path.abspath(__file__))+'\\characters.json'
filename_talents = os.path.dirname(os.path.abspath(__file__))+'\\talents.json'

json_data = {} # JSON data for character info
json_talents = {} # JSON data for talents



def load_json():
    global filename
    global filename_talents
    global json_data
    global json_talents
    
    # Check if the file exists, if not create it
    if not os.path.exists(filename):
        print("WARNING: characters.json file not found, creating a new one...")
        with open(filename, 'w') as file:
            json.dump({}, file) # Creates an empty JSON file
    # Load the JSON file into json_data
    with open(filename, 'r') as file:
        json_data = json.load(file)



    # Ensure all character data is valid
    for character in json_data:
        character_fix(character,True)



    # Check if the file exists before loading talents
    if not os.path.exists(filename_talents):
         print("WARNING: talents.json file not found, cannot load talents")
    else:
        # Load the talents JSON file into json_talents
        with open(filename_talents, 'r') as file:
            json_talents = json.load(file)

        format_talents()



# Save the json_data back to the JSON file
def save_json():
    with open(filename, 'w') as file:
        json.dump(json_data, file, indent=4) # Indent = 4 to make it look nice :)



#endregion ----------------------------------------------------------------

#region -------------------------------- import and format talents --------------------------------



# Determine rarity categories (empty_talents exists to copy from)
empty_talents = {
    "Common": {},
    "Rare": {},
    "Advanced": {},
    "Legendary": {}
}
all_talents = copy.deepcopy(empty_talents)

# Chance to get rarites out of 1 (in order of what to check first)
talent_categories = {
    "Legendary": 0.001, # 0.1%
    "Advanced": 0.01, # 1%
    "Rare": 0.1, # 10%
    "Common": 1 # 100%
}



def format_talents():
    global json_talents
    global all_talents

    for talent in json_talents:
        # Get the category of the talent
        category = json_talents[talent]["category"]

        # Check if the category is valid
        if category not in all_talents:
            #print(f"WARNING: Talent '{talent}' had an invalid category '{category}'! Skipping...")
            continue

        # Add the talent to the appropriate category
        all_talents[category][talent] = json_talents[talent]



#endregion ----------------------------------------------------------------

#region -------------------------------- character fix function --------------------------------



# Fix the character data to ensure it has all the required fields
def character_fix(character, warn=True):

    # Default character data
    default_character = {
        "owner": 0,
        "stats": {
            "Power": 0,
            "Strength": 0,
            "Fortitude": 0,
            "Agility": 0,
            "Intelligence": 0,
            "Willpower": 0,
            "Charisma": 0,
            "Light Weapon": 0,
            "Medium Weapon": 0,
            "Heavy Weapon": 0
        },
        "weapon": "Other",
        "aces": 0,
        "talents": [],
        "talents_burned": [],
        "talent_frozen": "None"
    }


    # Create a copy of the character to work with
    broken_character = copy.deepcopy(json_data[character])
    fixed_character = dictionary_fix(broken_character, default_character, warn)

    json_data[character] = fixed_character
    save_json()

    if warn and broken_character != fixed_character: print(f"WARNING: [character_fix] Fixed character with missing fields: {character}")
    return broken_character != fixed_character # Return True if anything was fixed



# Replace missing feilds in a dictionary with default values
def dictionary_fix(input_dictionary, backup_dictionary, warn=False):
    for key, value in backup_dictionary.items():
        if isinstance(value, dict):
            # If the value is a dictionary, recursively check it
            if key not in input_dictionary:
                if warn: print(f"    WARNING: [dictionary_fix] Missing key '{key}' in dictionary! Adding it...")
                input_dictionary[key] = backup_dictionary[key]
            else:
                dictionary_fix(input_dictionary[key], backup_dictionary[key],warn)
        elif key not in input_dictionary:
            if warn: print(f"    WARNING: [dictionary_fix] Missing key '{key}' in dictionary! Adding it...")
            input_dictionary[key] = backup_dictionary[key]

    return input_dictionary



#endregion ----------------------------------------------------------------

#region -------------------------------- talent selection functions --------------------------------



def find_exclusive_talents(character):
    exclusive_talents = []
    for talent in json_data[character]['talents']:
        if talent in json_talents:
            exclusive_talents += json_talents[talent]['exclusive']
        else:
            print(f"ERROR [find_exclusive_talents]: Talent '{talent}' was not found in all_talents!")

    return exclusive_talents



# Check if character meets all prerequisites for a talent (they have the stats and don't already have it or have burned it)
def meets_prerequisites(talent, character, exclude_talents):
    
    # Get prerequisites of the talent
    prerequisites = json_talents[talent]['prerequisites'].items()

    # Check if character meets all prerequisites
    meets_stats = all(
        json_data[character]['stats'].get(stat, 0) >= value
        for stat, value in prerequisites
    )



    # Check if you have all the required talents (useing subset notation)
    has_requirements = set(json_data[character]['talents']) >= set(json_talents[talent]['requires'])



    #find the exclusive talents
    exclusive_talents = find_exclusive_talents(character)

    # Check if the character already has the talent/burned it/froze it/can't have it or if it was already chosen
    disallowed = talent in json_data[character]['talents']+json_data[character]['talents_burned']+exclusive_talents+exclude_talents

    right_weapon = (json_talents[talent]['weapon'] == json_data[character]['weapon']) or (json_talents[talent]['weapon'] == "")

    return meets_stats and has_requirements and not disallowed and right_weapon



def get_valid_talents(character, exclude_talents):
    valid_talents = copy.deepcopy(empty_talents)
    for category in all_talents:
        for talent in all_talents[category]:
            if meets_prerequisites(talent, character, exclude_talents):
                valid_talents[category][talent] = all_talents[category][talent]

    return valid_talents



# Select a random valid talent not in the list based on rarity
def select_random_talent(character, exclude_talents):

    # Generate list of valid talents
    valid_talents = get_valid_talents(character, exclude_talents)

    # Convert talent_categores to an array in order of rarity (more rare checked first)
    talent_categories_list = [ key for (key, item) in sorted(talent_categories.items(),key=(lambda item: item[1])) ]

    roll = random.random() # Random between 0 and 1

    for i, category in enumerate(talent_categories_list):
        
        # Check if there are no more talents left after this category
        none_left = all(c == {} for c in talent_categories_list[i+1:])

        chance = talent_categories[category] # Get the chance of this category

        # If you hit the roll (smaller than the probability) or if this is the last category
        if roll <= chance or none_left:
            # Select a random talent from the category if not empty
            if valid_talents[category]:
                return random.choice(list(valid_talents[category].keys()))
            else:
                return -1 # No talents left



#endregion ----------------------------------------------------------------










#region -------------------------------- discord bot setup --------------------------------



intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)



@bot.event
async def on_ready(): # On startup
    print(f'Bot connected as {bot.user}')
    load_json()
    try:
        synced = await bot.tree.sync()
        synced = await bot.tree.sync(guild=discord.Object(id=server_id)) # Fast sync
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")



#endregion ----------------------------------------------------------------

#region -------------------------------- deepwoken_reload --------------------------------
@bot.tree.command(name="deepwoken_reload", description="Reloads all the files")
@app_commands.guilds(discord.Object(id=server_id))
async def deepwoken_reload(interaction: discord.Interaction):
    # Reload the JSON file
    load_json()
    await interaction.response.send_message("[deepwoken_reload] Files reloaded!")
#endregion ----------------------------------------------------------------

#region -------------------------------- deepwoken_help --------------------------------



@bot.tree.command(name="deepwoken_help", description="Lists available commands (only you will see this)")
@app_commands.guilds(discord.Object(id=server_id))
async def character_new(interaction: discord.Interaction):
    await interaction.response.send_message("[deepwoken_help] Nothing is here right now :(\nAsk @werdco", ephemeral=True)



#endregion ----------------------------------------------------------------

#region -------------------------------- character_add --------------------------------



@bot.tree.command(name="character_add", description="Adds a new character (you will be prompted for starting stats)")
@app_commands.guilds(discord.Object(id=server_id))
@app_commands.describe(name="Name of the character to add")
async def character_add(interaction: discord.Interaction, name: str):
    # Check if the character already exists
    if name in json_data:
        await interaction.response.send_message(f"[character_add] Character **{name}** already exists!")
        return
    
    # Create a new character with user id and default stats
    json_data[name] = {"owner": interaction.user.id}
    character_fix(name,False)
    save_json()

    await interaction.response.send_message(f"[character_add] Character **{name}** added successfully!")
    return



#endregion ----------------------------------------------------------------

#region -------------------------------- character_remove --------------------------------



@bot.tree.command(name="character_remove", description="Removes a spesified character (you must be the owner) (will ask for confirmation)")
@app_commands.guilds(discord.Object(id=server_id))
@app_commands.describe(name="Name of the character to remove")
async def character_remove(interaction: discord.Interaction, name: str):
    # Check if the character exists
    if name in json_data:
        if json_data[name]['owner'] != interaction.user.id:
            try: trueowner = await bot.fetch_user(json_data[name]['owner'])
            except: trueowner = "Unknown"
            await interaction.response.send_message(f"[character_remove] You cannot remove **{name}** as it belongs to **{trueowner}**!\nTry admin_character_remove")
        else:
            await interaction.response.send_message(f"[character_remove] Are you *sure* you want to remove character: **{name}** [Level: **{json_data[name]['stats']['Power']}**]?\n(This cannot be undone!)\n",view=RemovalWarning(name))
    else:
        await interaction.response.send_message(f"[character_remove] Character '**{name}**' does not exist!")

    return



@bot.tree.command(name="admin_character_remove", description="FORCIBLY removes a spesified character (will ask for confirmation)")
@app_commands.guilds(discord.Object(id=server_id))
@app_commands.describe(name="Name of the character to remove")
async def character_remove(interaction: discord.Interaction, name: str):
    # Check if the character exists
    if name in json_data:
        try: trueowner = await bot.fetch_user(json_data[name]['owner'])
        except: trueowner = "Unknown"
        await interaction.response.send_message(f"[admin_character_remove] Are you *sure* you want to remove character: **{name}**? [Level: **{json_data[name]['stats']['Power']}**] [Owner: **{trueowner}**]\n(This cannot be undone!)\n",view=RemovalWarning(name,True))
    else:
        await interaction.response.send_message(f"[admin_character_remove] Character '**{name}**' does not exist!")

    return



class RemovalWarning(discord.ui.View):
    def __init__(self, name: str, as_admin: bool = False):
        super().__init__()
        self.name = name
        self.admin_str = "admin_" if as_admin else ""
        self.timeout = None

        cancel_button = discord.ui.Button(label="NO, CANCEL!", style=discord.ButtonStyle.secondary)
        cancel_button.callback = self.cancel_remove
        accept_button = discord.ui.Button(label=f"Remove {self.name}", style=discord.ButtonStyle.danger)
        accept_button.callback = self.accept_remove

        self.add_item(cancel_button)
        self.add_item(accept_button)



    async def cancel_remove(self, interaction: discord.Interaction):
        await interaction.message.edit(content="[character_remove] character removal canceled", view=None)

    

    async def accept_remove(self, interaction: discord.Interaction):
        if (json_data.pop(self.name,-1) != -1):
            await interaction.message.edit(content=f"[{self.admin_str}character_remove] Removed character: **{self.name}**", view=None)
        else:
            await interaction.message.edit(content=f"[{self.admin_str}character_remove] Failed to remove character: '**{self.name}**'! (was probobly already removed)", view=None)
        save_json()



#endregion ----------------------------------------------------------------

#region -------------------------------- character_list --------------------------------



@bot.tree.command(name="character_list", description="Lists all stored characters")
@app_commands.guilds(discord.Object(id=server_id))
async def character_list(interaction: discord.Interaction):
    
    
    if  len(json_data) > 0:
        list_message = f"[character_list] List of characters:\n"
        for character in json_data:
            try: trueowner = await bot.fetch_user(json_data[character]['owner'])
            except: trueowner = "Unknown"
            list_message += f"\n**{character}** [Level: **{json_data[character]['stats']['Power']}**] [Owner: **{trueowner}**]"
        await interaction.response.send_message(list_message)
    else:
        await interaction.response.send_message("[character_list] There are currently no characters")
    
    return



#endregion ----------------------------------------------------------------

#region -------------------------------- character_dump --------------------------------



@bot.tree.command(name="character_dump", description="Dumps entire characters.json file")
@app_commands.guilds(discord.Object(id=server_id))
async def character_dump(interaction: discord.Interaction):
    load_json()
    # Send characters.json file
    if os.path.exists(filename):
        await interaction.response.send_message("[character_dump] Current characters.json file:", file=discord.File(filename))
    else:
        print("ERROR: characters.json file not found when trying to dump!")
        await interaction.response.send_message(f"[character_dump] ERROR: Missing characters.json file!\nPlease ask **{ownername}** to restart the bot.")
    return



#endregion ----------------------------------------------------------------

#region -------------------------------- character_info --------------------------------



@bot.tree.command(name="character_info", description="Gets info on a character (like stats and talents)")
@app_commands.guilds(discord.Object(id=server_id))
@app_commands.describe(name="Name of the character to get info of")
async def character_info(interaction: discord.Interaction, name: str):
    # Check if the character exists
    if name in json_data:
        info_message = f"[character_info] Info for character **{name}**:"

        # Get the character's basic info
        try: trueowner = await bot.fetch_user(json_data[name]['owner'])
        except: trueowner = "Unknown"
        info_message += f"\n\nOwned by **{trueowner}**"
        info_message += f"\nLevel (power): **{json_data[name]['stats']['Power']}**"
        
        # Get the character's stats
        info_message += f"\n\n\n\nStrength: **{json_data[name]['stats']['Strength']}**"
        info_message += f"\nFortitude: **{json_data[name]['stats']['Fortitude']}**"
        info_message += f"\nAgility: **{json_data[name]['stats']['Agility']}**"
        info_message += f"\nIntelligence: **{json_data[name]['stats']['Intelligence']}**"
        info_message += f"\nWillpower: **{json_data[name]['stats']['Willpower']}**"
        info_message += f"\nCharisma: **{json_data[name]['stats']['Charisma']}**"

        info_message += f"\n\nLight Weapon: **{json_data[name]['stats']['Light Weapon']}**"
        info_message += f"\nMedium Weapon: **{json_data[name]['stats']['Medium Weapon']}**"
        info_message += f"\nHeavy Weapon: **{json_data[name]['stats']['Heavy Weapon']}**"

        # Error if any unexpected stats are found
        expected_stats = ['Power', 'Strength', 'Fortitude', 'Agility', 'Intelligence', 'Willpower', 'Charisma', 'Light Weapon', 'Medium Weapon', 'Heavy Weapon']
        if any(stat not in expected_stats for stat in json_data[name]['stats']):
            info_message += f"\n\nWARNING - UNEXPECTED STAT(S) FOUND:\n**{json_data[name]['stats']}**\n"

        # Get the character's weapon
        info_message += f"\n\n\nCurrent weapon: **{json_data[name]['weapon']}**\n"
        # Check if the weapon is valid
        if json_data[name]['weapon'] not in ['Dagger', 'Spear', 'Fists', 'Rapier', 'Shield', 'Heavy', 'Greatsword', 'Greathammer', 'Other']:
            info_message += f"\n\nWARNING - INVALID WEAPON!**\n"

        
        # Get the character's talents
        if len(json_data[name]['talents']) > 0:
            info_message += f"\n\n\nTalents:\n"
            for talent in json_data[name]['talents']:
                info_message += f"\n**{talent}** [{json_talents[talent]['category']}]"
        else:
            info_message += f"\n\n\nCharacter has no talents\n"

        info_message += f"\n\n\n\nAces: **{json_data[name]['aces']}**\n"

        frozen_talent = json_data[name]['talent_frozen']
        if frozen_talent != "None":
            info_message += f"\nFrozen talent: **{frozen_talent}** [{json_talents[frozen_talent]['category']}]\n"
        else:
            info_message += "\nNo talent frozen\n"
        
        exclusive_talents = json_data[name]['talents_burned'] + find_exclusive_talents(name)
        if len(exclusive_talents) > 0:
            info_message += f"\n\n\nTalents burned or otherwise unobtainable (exclusive, etc.):\n"
            for talent in exclusive_talents:
                info_message += f"\n**{talent}** [{json_talents[talent]['category']}]"
        else:
            info_message += f"\nCharacter has not burned any talents\n"

        # Error if any unexpected info found
        expected_info = ['owner', 'stats', 'weapon', 'talents', 'aces', 'talents_burned', 'talent_frozen']
        if any(info not in expected_info for info in json_data[name]):
            info_message += f"\n\n\nWARNING - UNEXPECTED INFO FOUND:\n**{json_data[name]}**\n"


        await interaction.response.send_message(info_message)
    else:
        await interaction.response.send_message(f"[character_info] Character '**{name}**' does not exist!")
    
    return

@bot.tree.command(name="character_info_dump", description="Dumps all JSON info on a character (like stats and talents)")
@app_commands.guilds(discord.Object(id=server_id))
@app_commands.describe(name="Name of the character to dump info of")
async def character_info_dump(interaction: discord.Interaction, name: str):
    # Check if the character exists
    if name in json_data:
        info_message = f"[character_info_dump] Info dump for character **{name}**:\n"
        info_message += f"```json\n{json.dumps(json_data[name], indent=4)}\n```" # Use a code block to dump the JSON data
        await interaction.response.send_message(info_message)
    else:
        await interaction.response.send_message(f"[character_info_dump] Character '**{name}**' does not exist!")
    
    return




#endregion ----------------------------------------------------------------

#region -------------------------------- character_edit --------------------------------



@bot.tree.command(name="character_edit", description="Allows you to edit a character's stats and talents (you must be the owner)")
@app_commands.guilds(discord.Object(id=server_id))
@app_commands.describe(name="Name of the character to edit")
async def character_info(interaction: discord.Interaction, name: str):
    # Check if the character exists
    if name in json_data:
        if json_data[name]['owner'] != interaction.user.id:
            try: trueowner = await bot.fetch_user(json_data[name]['owner'])
            except: trueowner = "Unknown"
            await interaction.response.send_message(f"[character_edit] You cannot edit **{name}** as it belongs to **{trueowner}**!\nTry admin_character_edit")
        else:
            info_message = f"[character_edit] Editing character **{name}**:"

            # Get the character's basic info
            try: trueowner = await bot.fetch_user(json_data[name]['owner'])
            except: trueowner = "Unknown"
            info_message += f"\n\nOwned by **{trueowner}**"
            info_message += f"\nLevel (power): **{json_data[name]['stats']['Power']}**"
            
            # Get the character's stats
            info_message += f"\n\n\n\nStrength: **{json_data[name]['stats']['Strength']}**"
            info_message += f"\nFortitude: **{json_data[name]['stats']['Fortitude']}**"
            info_message += f"\nAgility: **{json_data[name]['stats']['Agility']}**"
            info_message += f"\nIntelligence: **{json_data[name]['stats']['Intelligence']}**"
            info_message += f"\nWillpower: **{json_data[name]['stats']['Willpower']}**"
            info_message += f"\nCharisma: **{json_data[name]['stats']['Charisma']}**"

            info_message += f"\n\nLight Weapon: **{json_data[name]['stats']['Light Weapon']}**"
            info_message += f"\nMedium Weapon: **{json_data[name]['stats']['Medium Weapon']}**"
            info_message += f"\nHeavy Weapon: **{json_data[name]['stats']['Heavy Weapon']}**"

            await interaction.response.send_message(info_message)
    else:
        await interaction.response.send_message(f"[character_edit] Character '**{name}**' does not exist!")
    
    return



#endregion ----------------------------------------------------------------

#region -------------------------------- character_levelup --------------------------------



@bot.tree.command(name="character_levelup", description="Levels up a character (you must be the owner) (will ask for confirmation)")
@app_commands.guilds(discord.Object(id=server_id))
@app_commands.describe(name="Name of the character to level up")
async def character_levelup(interaction: discord.Interaction, name: str):
    # Check if the character exists
    if name in json_data:
        try: trueowner = await bot.fetch_user(json_data[name]['owner'])
        except: trueowner = "Unknown"

        if json_data[name]['owner'] != interaction.user.id:
            await interaction.response.send_message(f"[character_levelup] You cannot level up **{name}** as it belongs to **{trueowner}**!\nTry admin_character_edit")
        else:
            # Level up the character
            ui = LevelupConfirm(name,trueowner)
            await interaction.response.send_message(ui.levelup_preview(),view=ui)
    else:
        await interaction.response.send_message(f"[character_levelup] Character '**{name}**' does not exist!")

    return

@app_commands.describe(name="Name of the character to edit")
async def character_edit(interaction: discord.Interaction, name: str):
    # Check if the character exists
    if name in json_data:
        if json_data[name]['owner'] != interaction.user.id:
            try: trueowner = await bot.fetch_user(json_data[name]['owner'])
            except: trueowner = "Unknown"
            await interaction.response.send_message(f"[character_edit] You cannot edit **{name}** as it belongs to **{trueowner}**!\nTry admin_character_edit")
        else:
            info_message = f"[character_edit] Editing character **{name}**:"

            # Get the character's basic info
            try: trueowner = await bot.fetch_user(json_data[name]['owner'])
            except: trueowner = "Unknown"
            info_message += f"\n\nOwned by **{trueowner}**"
            info_message += f"\nLevel (power): **{json_data[name]['stats']['Power']}**"
            
            # Get the character's stats
            info_message += f"\n\n\n\nStrength: **{json_data[name]['stats']['Strength']}**"
            info_message += f"\nFortitude: **{json_data[name]['stats']['Fortitude']}**"
            info_message += f"\nAgility: **{json_data[name]['stats']['Agility']}**"
            info_message += f"\nIntelligence: **{json_data[name]['stats']['Intelligence']}**"
            info_message += f"\nWillpower: **{json_data[name]['stats']['Willpower']}**"
            info_message += f"\nCharisma: **{json_data[name]['stats']['Charisma']}**"

            info_message += f"\n\nLight Weapon: **{json_data[name]['stats']['Light Weapon']}**"
            info_message += f"\nMedium Weapon: **{json_data[name]['stats']['Medium Weapon']}**"
            info_message += f"\nHeavy Weapon: **{json_data[name]['stats']['Heavy Weapon']}**"

            await interaction.response.send_message(info_message)
    else:
        await interaction.response.send_message(f"[character_edit] Character '**{name}**' does not exist!")
    
    return

class IntModal1(discord.ui.Modal, title="Enter Integer Values"):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.values = parent.delta_stats[0:5]
        self.val1 = discord.ui.TextInput(label="Strength", default=str(self.values[0]), placeholder="Enter an integer", required=True)
        self.val2 = discord.ui.TextInput(label="Fortitude", default=str(self.values[1]), placeholder="Enter an integer", required=True)
        self.val3 = discord.ui.TextInput(label="Agility", default=str(self.values[2]), placeholder="Enter an integer", required=True)
        self.val4 = discord.ui.TextInput(label="Intelligence", default=str(self.values[3]), placeholder="Enter an integer", required=True)
        self.val5 = discord.ui.TextInput(label="Willpower", default=str(self.values[4]), placeholder="Enter an integer", required=True)

        self.add_item(self.val1)
        self.add_item(self.val2)
        self.add_item(self.val3)
        self.add_item(self.val4)
        self.add_item(self.val5)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.values = [int(self.val1.value), int(self.val2.value), int(self.val3.value), int(self.val4.value), int(self.val5.value)]
            self.parent.delta_stats[:5] = self.values
            await interaction.message.edit(content=self.parent.levelup_preview(),view=self.parent)
            await interaction.response.defer()
        except ValueError:
            await interaction.response.send_message("[character_levelup page 1] ERROR: Please enter valid integers.", ephemeral=True)

class IntModal2(discord.ui.Modal, title="Enter Integer Values"):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.values = parent.delta_stats[5:9]
        self.val1 = discord.ui.TextInput(label="Charisma", default=str(self.values[0]), placeholder="Enter an integer", required=True)
        self.val2 = discord.ui.TextInput(label="Light Weapon", default=str(self.values[1]), placeholder="Enter an integer", required=True)
        self.val3 = discord.ui.TextInput(label="Medium Weapon", default=str(self.values[2]), placeholder="Enter an integer", required=True)
        self.val4 = discord.ui.TextInput(label="Heavy Weapon", default=str(self.values[3]), placeholder="Enter an integer", required=True)
        #self.val5 = discord.ui.TextInput(label="Aces", default=str(self.values[4]), placeholder="Enter an integer", required=True)

        self.add_item(self.val1)
        self.add_item(self.val2)
        self.add_item(self.val3)
        self.add_item(self.val4)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.values = [int(self.val1.value), int(self.val2.value), int(self.val3.value), int(self.val4.value)]
            self.parent.delta_stats[5:9] = self.values
            await interaction.message.edit(content=self.parent.levelup_preview(),view=self.parent)
            await interaction.response.defer()
        except ValueError:
            await interaction.response.send_message("[character_levelup page 2] ERROR: Please enter valid integers.", ephemeral=True)

class WeaponSelect(discord.ui.Select):
    def __init__(self, parent, choices: list[str], name: str):
        self.name = name
        self.parent = parent
        options = [
            discord.SelectOption(
                label=choice,
                value=choice,
                default=(choice == parent.weapon) # Default to item currently selected
            )
            for choice in choices
        ]
        super().__init__(
            placeholder=f"What weapon are you using?",
            options=options
        )
    async def callback(self, interaction: discord.Interaction): # Return selection
        self.current_value = self.values[0]  # new selected value

        for option in self.options:
            option.default = (option.value == self.current_value)
        
        self.parent.weapon = self.current_value
        await interaction.response.defer()
        await interaction.message.edit(content=self.parent.levelup_preview(), view=self.parent)
        return self.values[0]

class LevelupConfirm(discord.ui.View):
    def __init__(self, name: str, trueowner: str = "Unknown"):
        super().__init__()
        self.name = name
        self.trueowner = trueowner
        self.timeout = None

        self.delta_stats = [0,0,0,0,0,0,0,0,0]
        self.weapon = json_data[self.name]['weapon']
        self.delta_aces = 0
        if (json_data[self.name]['stats']['Power'] + 1) % 5 == 0: # Every 5 levels you get an ace
            self.delta_aces = 1
        if (json_data[self.name]['stats']['Power'] + 1) == 2: # Get 2 aces at level 2
            self.delta_aces = 2
        

        self.cancel_button = discord.ui.Button(label="NO, CANCEL!", style=discord.ButtonStyle.secondary)
        self.cancel_button.callback = self.cancel_levelup
        self.accept_button = discord.ui.Button(label=f"Stat points left: 15", style=discord.ButtonStyle.success,disabled=True)
        self.accept_button.callback = self.accept_levelup
        self.select_menu = WeaponSelect(self, ["Dagger", "Spear", "Fists", "Rapier", "Shield", "Heavy", "Greatsword", "Greathammer", "Other"], self.name)

        self.add_item(self.select_menu)
        self.add_item(self.cancel_button)
        self.add_item(self.accept_button)


    def levelup_preview(self):
        message_content = f"[character_levelup] Leveled-up character: **{self.name}**"
        
        # Get the character's basic info
        message_content += f"\n\nOwned by **{self.trueowner}**"
        message_content += f"\nLevel (power): {json_data[self.name]['stats']['Power']} → **{json_data[self.name]['stats']['Power'] + 1}**"
        message_content += f"\nAces: {json_data[self.name]['aces']} → **{json_data[self.name]['aces'] + self.delta_aces}**"
            
        # Get the character's stats
        message_content += f"\n\n\n\nStrength: {json_data[self.name]['stats']['Strength']} → **{json_data[self.name]['stats']['Strength']+self.delta_stats[0]}** (+{self.delta_stats[0]})"
        message_content += f"\nFortitude: {json_data[self.name]['stats']['Fortitude']} → **{json_data[self.name]['stats']['Fortitude']+self.delta_stats[1]}** (+{self.delta_stats[1]})"
        message_content += f"\nAgility: {json_data[self.name]['stats']['Agility']} → **{json_data[self.name]['stats']['Agility']+self.delta_stats[2]}** (+{self.delta_stats[2]})"
        message_content += f"\nIntelligence: {json_data[self.name]['stats']['Intelligence']} → **{json_data[self.name]['stats']['Intelligence']+self.delta_stats[3]}** (+{self.delta_stats[3]})"
        message_content += f"\nWillpower: {json_data[self.name]['stats']['Willpower']} → **{json_data[self.name]['stats']['Willpower']+self.delta_stats[4]}** (+{self.delta_stats[4]})"
        message_content += f"\nCharisma: {json_data[self.name]['stats']['Charisma']} → **{json_data[self.name]['stats']['Charisma']+self.delta_stats[5]}** (+{self.delta_stats[5]})"

        message_content += f"\n\nLight Weapon: {json_data[self.name]['stats']['Light Weapon']} → **{json_data[self.name]['stats']['Light Weapon']+self.delta_stats[6]}** (+{self.delta_stats[6]})"
        message_content += f"\nMedium Weapon: {json_data[self.name]['stats']['Medium Weapon']} → **{json_data[self.name]['stats']['Medium Weapon']+self.delta_stats[7]}** (+{self.delta_stats[7]})"
        message_content += f"\nHeavy Weapon: {json_data[self.name]['stats']['Heavy Weapon']} → **{json_data[self.name]['stats']['Heavy Weapon']+self.delta_stats[8]}** (+{self.delta_stats[8]})"
        if (self.select_menu.values):
            if (json_data[self.name]['weapon'] != self.select_menu.values[0]):
                message_content += f"\n\n{json_data[self.name]['weapon']} → **{self.weapon}**"

        if sum(self.delta_stats) == 15:
            self.accept_button.disabled = False
            self.accept_button.label = f"Level up {self.name}"
        elif sum(self.delta_stats) < 15:
            self.accept_button.disabled = True
            self.accept_button.label = f"Stat points left: {15-sum(self.delta_stats)}"
        else:
            self.accept_button.disabled = True
            self.accept_button.label = f"Stat points over: {sum(self.delta_stats)-15}"

        return message_content

    async def cancel_levelup(self, interaction: discord.Interaction):
        await interaction.message.edit(content="[character_levelup] Character level up canceled", view=None)


    async def accept_levelup(self, interaction: discord.Interaction):
        
        await interaction.message.edit(content=self.levelup_preview(), view=None)

        json_data[self.name]['stats']['Power'] += 1
        json_data[self.name]['aces'] += self.delta_aces
        json_data[self.name]['stats']['Strength'] += self.delta_stats[0]
        json_data[self.name]['stats']['Fortitude'] += self.delta_stats[1]
        json_data[self.name]['stats']['Agility'] += self.delta_stats[2]
        json_data[self.name]['stats']['Intelligence'] += self.delta_stats[3]
        json_data[self.name]['stats']['Willpower'] += self.delta_stats[4]
        json_data[self.name]['stats']['Charisma'] += self.delta_stats[5]
        json_data[self.name]['stats']['Light Weapon'] += self.delta_stats[6]
        json_data[self.name]['stats']['Medium Weapon'] += self.delta_stats[7]
        json_data[self.name]['stats']['Heavy Weapon'] += self.delta_stats[8]

        json_data[self.name]['weapon'] = self.weapon # Set the weapon to the selected one
        save_json()

    @discord.ui.button(label="Edit stats page 1", style=discord.ButtonStyle.primary)
    async def open_modal_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IntModal1(self))

    @discord.ui.button(label="Edit stats page 2", style=discord.ButtonStyle.primary)
    async def open_modal_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IntModal2(self))



#endregion ----------------------------------------------------------------

#region -------------------------------- talent_list --------------------------------



@bot.tree.command(name="talent_info", description="Gives info about a talent")
@app_commands.guilds(discord.Object(id=server_id))
async def talent_info(interaction: discord.Interaction, talent: str):
    # Check if any talents are loaded
    if (all_talents != empty_talents):
        for category in all_talents:
            # If tallent found
            if talent in all_talents[category]:
                list_message = f"[talent_info]:\n"
                list_message += f"\n**{talent}** [{category}] - {all_talents[category][talent]['description']}\n"
                if all_talents[category][talent]['prerequisites']: list_message += f"    Prerequisites: {', '.join(f'{k}: {v}' for k, v in all_talents[category][talent]['prerequisites'].items())}\n"
                if all_talents[category][talent]['requires']: list_message += f"    Requires: {all_talents[category][talent]['requires']}\n"
                if all_talents[category][talent]['exclusive']: list_message += f"    Exclusive: {all_talents[category][talent]['exclusive']}\n"
                if all_talents[category][talent]['weapon']: list_message += f"    Weapon needed: {all_talents[category][talent]['weapon']}\n"
                await interaction.response.send_message(list_message)
                return
        await interaction.response.send_message(f"[talent_info] ERROR: Talent '**{talent}**' not found! Use talent_list for a list of all talents")
    else:
        await interaction.response.send_message("[talent_info] ERROR: No talents loaded! Try talent_dump?")
    return



@bot.tree.command(name="talent_list", description="Lists all talents (ghost message)")
@app_commands.guilds(discord.Object(id=server_id))
async def talent_list(interaction: discord.Interaction):
    soft_message_limit = 2000-100 # Discord message limit = 2000; leave 100 as a buffer
    
    # Check if any talents are loaded
    if (all_talents != empty_talents):
        await interaction.response.send_message("[talent_list] WARN: There are a lot of talents! They have had to be split into multiple messages.\nList of talents:\n",ephemeral=True)
        list_message = ""
        for category in all_talents:
            list_message += f"\n\n\n\n**{category}**:\n"
            for talent in all_talents[category]:
                list_message += f"\n{talent}"

                if (len(list_message) > soft_message_limit):
                    list_message += f"\n\n..." # Add a break if the message is too long
                    await interaction.followup.send(list_message,ephemeral=True)
                    list_message = ""
        if (list_message != ""):
            await interaction.followup.send(list_message,ephemeral=True)

    else:
        await interaction.response.send_message("[talent_list] ERROR: No talents loaded! Try talent_dump?",ephemeral=True)
    return



@bot.tree.command(name="talent_list_available", description="Lists all talents a character can currently roll (ghost message)")
@app_commands.guilds(discord.Object(id=server_id))
async def talent_list_available(interaction: discord.Interaction, character: str):
    soft_message_limit = 2000-100 # Discord message limit = 2000; leave 100 as a buffer
    
    # Check if the character exists
    if character in json_data:

        # Get list of available talents
        available_talents = get_valid_talents(character, [json_data[character]['talent_frozen']])
        frozen_talent = json_data[character]['talent_frozen']


        # List available talents if character has any
        if available_talents or frozen_talent != "None":
            list_message = f"[talent_list_available] List of talents available to be rolled by **{character}**:\n"

            # Check for frozen talent
            if frozen_talent != "None":
                
                if meets_prerequisites(frozen_talent,character):
                    list_message += f"\nFrozen talent (guarenteed):\n"
                else:
                    list_message += f"\nFrozen talent (CONDITIONS NOT MET - will not receive):\n"
                
                list_message += f"\n**{frozen_talent}** [{json_talents[frozen_talent]['category']}]\n"
                #if json_talents[frozen_talent]['prerequisites']: list_message += f"        Prerequisites: {', '.join(f'{k}: {v}' for k, v in json_talents[frozen_talent]['prerequisites'].items())}\n"
                #if json_talents[frozen_talent]['requires']: list_message += f"        Requires: {json_talents[frozen_talent]['requires']}\n"
                #if json_talents[frozen_talent]['exclusive']: list_message += f"        Exclusive: {json_talents[frozen_talent]['exclusive']}\n\n\n\n"



            # Start listing the rest
            if available_talents != empty_talents: # If there are any talents available
                list_message += "\nWARN: There are a lot of talents! They have had to be split into multiple messages.\n"
                await interaction.response.send_message(list_message,ephemeral=True)
                list_message = ""

                for category in available_talents:
                    if available_talents[category] != {}: # If there are any talents in the category
                        list_message += f"\n\n\n\n**{category}**:\n"

                        for talent in available_talents[category]:
                            if talent != frozen_talent: # Don't list the frozen talent again
                                list_message += f"\n{talent}"
                                #if json_talents[talent]['prerequisites']: list_message += f"    Prerequisites: {', '.join(f'{k}: {v}' for k, v in json_talents[talent]['prerequisites'].items())}\n"
                                #if json_talents[talent]['requires']: list_message += f"    Requires: {json_talents[talent]['requires']}\n"
                                #if json_talents[talent]['exclusive']: list_message += f"    Exclusive: {json_talents[talent]['exclusive']}\n"
                                if (len(list_message) > soft_message_limit):
                                    list_message += f"\n\n..." # Add a break if the message is too long
                                    await interaction.followup.send(list_message,ephemeral=True)
                                    list_message = ""
                if (list_message != ""):
                    await interaction.followup.send(list_message,ephemeral=True)
            else:
                list_message += f"\n[talent_list_available] Character **{character}** has no talents available :("
                await interaction.response.send_message(list_message,ephemeral=True)
            
    else:
        await interaction.response.send_message(f"[talent_list_available] Character '**{character}**' does not exist!",ephemeral=True)

    return



@bot.tree.command(name="talent_dump", description="Dumps entire talents.json file")
@app_commands.guilds(discord.Object(id=server_id))
async def talents_dump(interaction: discord.Interaction):
    load_json()
    # Send talents.json file
    if os.path.exists(filename_talents):
        await interaction.response.send_message("[talent_dump] Current talents.json file:", file=discord.File(filename_talents))
    else:
        print("ERROR: talents.json file not found when trying to dump!")
        await interaction.response.send_message(f"[talent_dump] ERROR: Missing talents.json file!\nPlease ask **{ownername}** to restart the bot.")
    return



#endregion ----------------------------------------------------------------

#region -------------------------------- talent_roll --------------------------------



@bot.tree.command(name="talent_roll", description="Rolls a set of 5 talents to chose from (cancelable)")
@app_commands.guilds(discord.Object(id=server_id))
@app_commands.describe(character="Name of the character to remove")
async def roll_talents(interaction: discord.Interaction, character: str):
    # Ensure the character exists
    if character not in json_data:
        await interaction.response.send_message(f"[talent_roll] Character '**{character}**' does not exist!")
        return

    # Generate 5 random valid unique talents. Put in array random talents
    number_of_talents = 5
    random_talents = []
    frozen_talent = json_data[character]['talent_frozen']
    for n in range(number_of_talents):
        # Make the first one the frozen talent
        next_talent = frozen_talent if n == 0 and frozen_talent != "None" else select_random_talent(character, random_talents)
        random_talents.append(next_talent)

    await FullSelection(interaction,character,random_talents).send_messages()

class FullSelection():
    def __init__(self, interaction: discord.Interaction, character: str, random_talents: list[str]):
        self.interaction = interaction
        self.character = character
        self.random_talents = random_talents

        self.accepted = 0 # 0 = Picking; 1 = Confirmed; 2 = Canceled
        self.did_generate = False # If any talents were generated
        self.talent_embeds = [None,None,None,None,None] # Store the embeds for each talent
        self.init_message = None
        self.talent_messages = [None,None,None,None,None] # Store the messages for each talent
        self.confirm_message = None # Store the confirm message

        self.old_aces = json_data[character]['aces'] # Store aces count
        self.temp_aces = self.old_aces
        self.temp_taken = None
        if (json_data[character]['talent_frozen'] != "None"):
            self.old_frozen = json_data[character]['talent_frozen']
        else:
            self.old_frozen = None
        self.temp_frozen = self.old_frozen
        self.temp_burned = []

        # Declare rarity colors
        self.rarity_colors = {
            "None": discord.Color.from_rgb(0, 0, 0), # Black
            "Common": discord.Color.from_rgb(98, 97, 90), # Gray
            "Rare": discord.Color.from_rgb(137, 96, 96), # Red
            "Advanced": discord.Color.from_rgb(144, 111, 147), # Purple
        }



    async def send_messages(self):
        # Send message
        self.init_message = await self.interaction.response.send_message(f"[talent_roll] Rolling talents for **{self.character}**:\nYou have **{self.temp_aces}** aces left to use.")
        for i, talent_name in enumerate(self.random_talents):
            if (talent_name != -1):
                # Send embed for each talent
                talent = json_talents[talent_name]
                embed = discord.Embed(title=talent_name, description=talent['category'], color=self.rarity_colors[talent['category']])
                if talent["prerequisites"]: embed.add_field(name="Prerequisites", value=", ".join(f"{k}: {v}" for k, v in talent["prerequisites"].items()), inline=False)
                if talent["requires"]: embed.add_field(name="Requires", value=", ".join(f"{k}" for k in talent["requires"]), inline=False)
                if talent["exclusive"]: embed.add_field(name="Exclusive", value=", ".join(f"{k}" for k in talent["exclusive"]), inline=False)
                if talent["weapon"]: embed.add_field(name="Weapon", value=talent["weapon"], inline=False)
                embed.set_footer(text=f"Talent {i+1} of {len(self.random_talents)}")
                
                # Store the embed and message
                self.did_generate = True
                self.talent_embeds[i] = embed
                self.talent_messages[i] = await self.interaction.followup.send(embed=embed, view=TalentSelection(index=i,parent=self,character=self.character))
            else:
                # No talents available
                await self.interaction.followup.send(f"[roll_talents] **{self.character}** has no more available talents")
                break

        if self.did_generate: # If any talents were generated, ask to confirm
            self.confirm_message = await self.interaction.followup.send(f"[roll_talents] Confirm selection for character: **{self.character}**:\nAces: **{self.temp_aces}**\n", view=discord.ui.View(timeout=None))
            await self.reload_messages()



    async def reload_messages(self):
        # Verify choices
        if self.temp_taken == self.temp_frozen: self.temp_frozen = None
        if self.temp_taken in self.temp_burned: self.temp_burned.remove(self.temp_taken)
        if self.temp_frozen in self.temp_burned: self.temp_burned.remove(self.temp_frozen)
        self.temp_aces = self.old_aces-len(self.temp_burned)

        # Update ace counter
        init_message = await self.interaction.original_response()
        await init_message.edit(content=f"[talent_roll] Rolling talents for **{self.character}**:\nYou have **{self.temp_aces}** aces left to use.")

        # Reload the messages for the talents
        for i, random_talent in enumerate(self.random_talents):
            if self.talent_messages[i] is not None:
                card_heading = ""
                if self.temp_taken == random_talent:
                    card_heading = ":green_square: SELECTED :green_square: "
                if self.temp_frozen == random_talent:
                    card_heading = ":snowflake: FROZEN :snowflake: "
                if random_talent in self.temp_burned:
                    card_heading = ":fire: BURNED :fire: "
                await self.talent_messages[i].edit(content=card_heading,embed=self.talent_embeds[i], view=TalentSelection(parent=self, index=i, character=self.character))

        
        if self.confirm_message is not None:
            # Cancel message
            if self.accepted == 2:
                confirm_message_content = f"[talent_roll] Talent roll for **{self.character}** canceled!"
            else:
                # Confirm message
                if self.accepted == 1:
                    confirm_message_content = f"[talent_roll] Successfully confirmed talent selection for **{self.character}**:"
                else:
                    confirm_message_content = f"[talent_roll] Confirm selection for **{self.character}**:"

                # Aces
                if (self.temp_aces == json_data[self.character]['aces']):
                    confirm_message_content += f"\nAces: **{self.old_aces}**"
                else:
                    confirm_message_content += f"\nAces: {self.old_aces} → **{self.temp_aces}**"
                
                # Talents
                if (self.temp_taken is not None):
                    confirm_message_content += f"\nSelected talent: **{self.temp_taken}**"
                if (self.temp_frozen is not None):
                    confirm_message_content += f"\nFrozen talent: **{self.temp_frozen}**"
                if (len(self.temp_burned) > 0):
                    confirm_message_content += f"\nBurned talents: **{', '.join(self.temp_burned)}**"
            
            # Preview
            if self.accepted == 0:
                await self.confirm_message.edit(content=confirm_message_content,view=TalentConfirm(parent=self))
            else: # Final message
                await init_message.edit(content=confirm_message_content,view=None)
                await self.confirm_message.delete()
                for message in self.talent_messages:
                    await message.delete()





# Talent card class (contains name, info, and the selection buttons)
class TalentSelection(discord.ui.View):
    def __init__(self, parent: object, index: int, character: str):
        super().__init__(timeout=None)
        self.index = index
        self.character = character
        self.parent = parent # Reference to FullSelection()
        
        # Buttons
        self.take_button = discord.ui.Button(label="Take", style=discord.ButtonStyle.success)
        self.take_button.callback = self.take_talent
        self.burn_button = discord.ui.Button(label="Burn (costs 1 ace)", style=discord.ButtonStyle.danger, disabled=(json_data[self.character]['aces'] <= 0))
        self.burn_button.callback = self.burn_talent
        self.freeze_button = discord.ui.Button(label="Freeze (must have at least 1 ace)", style=discord.ButtonStyle.primary, disabled=(json_data[self.character]['aces'] <= 0))
        self.freeze_button.callback = self.freeze_talent

        

        if self.parent.temp_taken == self.parent.random_talents[self.index]: # Talent picked
            self.take_button.disabled = True
            self.burn_button.disabled = True
            self.freeze_button.disabled = True
        
        if self.parent.random_talents[self.index] in self.parent.temp_burned: # Talent burned
            self.burn_button.label = "Unburn (refund ace)"
        elif self.parent.temp_aces <= 0: # Can't burn
            self.burn_button.disabled = True
            self.burn_button.label = "Burn (no aces!)"
        
        if self.parent.temp_frozen == self.parent.random_talents[self.index]: # Talent frozen
            self.freeze_button.label = "Unfreeze"
            self.burn_button.disabled = True
        elif self.parent.temp_aces <= 0: # Can't freeze
            self.freeze_button.disabled = True
            self.freeze_button.label = "Freeze (no aces!)"

        self.add_item(self.take_button)
        self.add_item(self.burn_button)
        self.add_item(self.freeze_button)



    async def take_talent(self, interaction: discord.Interaction):
        self.parent.temp_taken = self.parent.random_talents[self.index]

        # Disable all buttons (precaution)
        #self.take_button.disabled = True
        self.burn_button.disabled = True
        self.freeze_button.disabled = True
        await self.parent.reload_messages()
        if not interaction.response.is_done():
            await interaction.response.defer()
    


    async def burn_talent(self, interaction: discord.Interaction):
        if self.parent.random_talents[self.index] not in self.parent.temp_burned:
            self.parent.temp_burned.append(self.parent.random_talents[self.index])
        else:
            self.parent.temp_burned.remove(self.parent.random_talents[self.index])
        # Disable all buttons (precaution)
        self.take_button.disabled = True
        #self.burn_button.disabled = True
        self.freeze_button.disabled = True
        await self.parent.reload_messages()
        if not interaction.response.is_done():
            await interaction.response.defer()



    async def freeze_talent(self, interaction: discord.Interaction):
        if self.parent.temp_frozen != self.parent.random_talents[self.index]:
            self.parent.temp_frozen = self.parent.random_talents[self.index]
        else:
            self.parent.temp_frozen = None

        # Disable all buttons (precaution)
        self.take_button.disabled = True
        self.burn_button.disabled = True
        #self.freeze_button.disabled = True
        await self.parent.reload_messages()
        if not interaction.response.is_done():
            await interaction.response.defer()



class TalentConfirm(discord.ui.View):
    def __init__(self, parent: FullSelection):
        super().__init__(timeout=None)
        self.parent = parent
        self.cancel_button = discord.ui.Button(label="NO, CANCEL!", style=discord.ButtonStyle.secondary)
        self.cancel_button.callback = self.cancel_selection
        self.confirm_button = discord.ui.Button(label="Confirm selection", style=discord.ButtonStyle.success)
        self.confirm_button.callback = self.confirm_selection

        if self.parent.temp_taken is None:
            self.confirm_button.disabled = True
            self.confirm_button.label = "No talent selected"

        self.add_item(self.cancel_button)
        self.add_item(self.confirm_button)

    async def confirm_selection(self, interaction: discord.Interaction):

        # Update character data
        json_data[self.parent.character]['aces'] = self.parent.old_aces-len(self.parent.temp_burned)
        json_data[self.parent.character]['talents'].append(self.parent.temp_taken)
        if self.parent.temp_frozen is not None:
            json_data[self.parent.character]['talent_frozen'] = self.parent.temp_frozen
        json_data[self.parent.character]['talents_burned'] += self.parent.temp_burned
        save_json()

        # Set accepted to True and reload
        self.parent.accepted = 1
        await self.parent.reload_messages() # Reload the messages to show final changes

    async def cancel_selection(self, interaction: discord.Interaction):
        # Cancel the selection
        self.parent.accepted = 2
        await self.parent.reload_messages()



#endregion ----------------------------------------------------------------










bot.run(bot_token)


