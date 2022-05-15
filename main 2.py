import threading
import discord
import json
import time
import random
from discord.ext import commands
from datetime import datetime


# Discord Bot's Token
bot_token = "OTUxNDU2MDYzMjUxNjkzNjE4.Yinugg.qolhys0B1JGNfX53DF3fm8QX6K8"


# Bot will get triggered to commands that start with "!"
bot = commands.Bot(command_prefix='!')


# Nested Dictionary to hold list of players that will play the game.
# Initially it is empty and players.json file must have '{}' to become a dictionary.
player_list = {}


global seconds
global msg_id
global is_time_up


# Let's us know that bot is ready to work.
@bot.event
async def on_ready():
    print('\nSystem_Msg:  Bot is ready to work!')


# Player object
class Player:

    # In order to create a player object; name, and id are required.
    # While creating the player object, we convert it to a dictionary in constructor.
    def __init__(self, name, player_id):
        self.name = name
        self.id = player_id

        # Check and add the created player to player_list nested dictionary.
        check_and_add_player(self)


# Checks user before adding it to list.
def check_and_add_player(selected_player):

    # We check if the given player is already in the list. If it is, we don't add it.
    if is_time_up == False:

        # Then we check if it is already in the list.
        if selected_player.name in player_list:
            print(f'\nError_Msg:  {selected_player.name} is already in the list!')

        # If not, we add the player to player_list.
        else:
            # Convert player object to a dictionary object.
            current_player = {
                'name': selected_player.name,
                'id': selected_player.id,
                'isAlive': True
            }

            # As a key value in the dictionary, I am using the id of the user.
            player_list[f'{selected_player.name}'] = current_player
            export_players_to_json(player_list)

            # To see the added player, I prompt a message to console.
            print(f'\nSuccess_Msg:  {selected_player.name} is added successfully to the list!')

    else:
        print('\nError_Msg:  Time is Up, user cannot join to the game.')


# Set message Id of embedded message globally.
def set_id(id):
    global msg_id
    msg_id = id


# Set how many seconds left globally.
def set_is_time_up(time_left):
    global is_time_up
    is_time_up = time_left


# Set seconds of embedded message globally.
def set_seconds(sec):
    global seconds
    seconds = sec


# Write the player_list nested dictionary to a json file named 'players'.
def export_players_to_json(player_list):

    # We handle the checks before the round starts.
    with open('players.json', 'w') as file:
        json.dump(player_list, file)
        file.close()
        print('\nSuccess_Msg:  player_list successfully exported to players.json')


# Update the players_list from json at beginning of each round.
def import_players_from_json():
    
    # Load json file to check. If file is empty, we must put {} to make it a dictionary.
    # Or we will get errors because alive_players won't be assigned as dictionary object.
    with open('players.json') as file:
        players = json.load(file)
        print('\nSuccess_Msg:  players imported successfulyy from players.json')

    return players


# Randomly choose players and make a list that only chosen player that will be in.
def prepare_players_for_game():

    print(f'\nSystem_Msg:  Preparing Players now!')
    
    # Update player_list from json.
    player_list = import_players_from_json()
    print(f'\nSuccess_Msg:   updated player_list {player_list}')

    # Keep alive players with their keys and values.
    alive_players = {}

    # Keep the name of the alive players in an array.
    alive_ones = []

    # Get players that are alive from the updated player list.
    for player_name, p_isAlive in player_list.items():
        for key in p_isAlive:
            if key == 'isAlive':
                if p_isAlive[key] == True:
                     print(f'\nSystem_Msg:  {player_name} is alive!')
                     alive_players[player_name] = player_list[player_name]
                     alive_ones.append(player_name)
                else:
                    print(f'\nSystem_Msg:  {player_name} is dead!')

    print('\nSystem_Msg:  alive ones array: ', alive_ones)

    choose_round_players(alive_players, alive_ones)


# Update the dead players on the player_list and export it
def update_players(round_players):

    player_list = import_players_from_json()
    for player_name, p_isAlive in round_players.items():
        for key in p_isAlive:
            if key == 'isAlive':
                if p_isAlive[key] == False:
                     print(f'\n {player_name} died')
                     player_list[player_name] = round_players[player_name]
                                
    print('\nSystem_Msg:  Round ended!')
    print('\nPlayer_list after:', player_list)
    export_players_to_json(player_list)
    make_new_round(player_list)


# If user clicks on check mark reaction, we enroll thr user to the game. 
@bot.event
async def on_raw_reaction_add(payload):
    if msg_id == payload.message_id:
        member = payload.member
        emoji = payload.emoji.name
        if member != bot.user:
            if emoji == '✅':
                player = Player(member.name, member.id)
            elif emoji == '❎':
                print(f'\nSystem_Msg:  {member.name} will not be participating in the game.')


# Play command, it can only run by Moderators.
@bot.command(name='play', pass_context=True)
@commands.has_role('Moderator')
async def on_message(ctx):

    global is_time_up
    is_time_up = False

    embed = discord.Embed(
      title='Click to join',
      description='In order to play the game, you need to join now',
      color =0xf55951,
      timestamp=datetime.now()
    )
  
    msg = await ctx.send(embed=embed)
    set_id(msg.id)

    await msg.add_reaction('✅')
    await msg.add_reaction('❎')
    threading.Thread(target = game_count_down).start()
    await sendEmbedMsg(ctx)
    

# We count down from 2 mins and get players to the pool, then we save them to json.
def game_count_down():
    
    global seconds
    global is_time_up
    is_time_up = False


    # t is seconds that we will count down from.
    t = 11

    while t > 0:
       
        # This converts seconds into mins
        mins, secs = divmod(t, 60)

        seconds = t
        set_seconds(seconds)

        # For testing purposes I format it and print it to seconds to console.
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")

        # This is how we count down.
        time.sleep(1)
        t -= 1

        if t != 0:
            is_time_up = False
            set_is_time_up(False)

        # Send an embed that indicates game is starting now!
        elif t == 0: 
            #add Dummy Players here!
            set_is_time_up(True)
            prepare_players_for_game()


# DONE TILL HERE
# *****************************************************************


# Randomly Chooses round players from Alive Players list. 
def choose_round_players(alive_players, alive_ones):

    # Calculate round count and choose round players accordingly.

    # Keep round players with their keys and values.
    round_players = {}

    # Keep the name of the playing players in an array.
    playing_ones = []

    # Picking 4 players from alive_ones and adding them to round_players.
    for i in range(0, 5):
        # -1 because arrays start from 0.
        rand_num = random.randint(0, len(alive_ones) - 1)
        # alive_ones[0] is 'osman', so the key
        key = alive_ones[rand_num]
        # round_players['osman'] = alive_ones['osman']
        round_players[key] = alive_players[key]
        # Now we added them to array with their keys(names).
        playing_ones.append(key)

    play_round
    print('\nSystem_Msg:  playing ones array: ', playing_ones)
    (round_players, playing_ones)  


# plays the round and kills some of the players
def play_round(round_players, playing_ones):

    print('\nSystem_Msg:  Round started!')

    # This is where we kill the half of the players every round.
    # Currently we have 4 players. 2-3 players must die each round and rest must survive.
    # Check the length of array before loop or fatal runtime error!
    for i in range(0, len(playing_ones)):
        rand_num = random.randint(0, 1000)
        if rand_num % 2 == 0:
            key = playing_ones[rand_num%4]
            round_players[key]['isAlive'] = False

    print('\nSystem_Msg:  round players: ', round_players)

    update_players(round_players)


# send embeded messages according to time left for the game.
async def sendEmbedMsg(ctx):
    ten = False
    five = False
    two = False

    embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)

    global seconds

    while seconds >= 0:
        if seconds == 10 and ten == False:
            ten = True
            embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
            embedVar.add_field(name="10", value="hi", inline=False)
            await ctx.channel.send(embed=embedVar)
        elif seconds == 5 and five == False:
            five = True
            embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
            embedVar.add_field(name="5", value="hi2", inline=False)
            await ctx.channel.send(embed=embedVar)
        elif seconds == 2 and two == False:
            two = True
            embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
            embedVar.add_field(name="2", value="hi3", inline=False)
            await ctx.channel.send(embed=embedVar)


# MUST BE ADJUSTED TILL HERE
# *****************************************************************


# Calculate how many rounds there will be according to player.
def calculate_round_count(initial_list):
    # calculate an est. value according to the player count

    round_count = -1
    player_count = len(initial_list) 

    #BURDAN DEVAM ET
    #round_count = 

    # if player_count > 20:
    #    round_count = 10
    # elif player_count > 10:
    #    round_count = 5
    # elif player_count > 5:
    #    round_count = 2
    
    print(f'\nSystem_Msg:  There will be {round_count} rounds.')
    return round_count


# IMPLEMENT IT
def make_new_round(player_list):
    # send round results with migration scenarios.
    # check alive ones
    # check for the last round.
    # choose round players according to est. round count and player count
    # play round
    # Implement game finished and publish winner.
    x = 5
    

# MUST BE IMPLEMENTED TILL HERE
# *****************************************************************


# To run the bot and make it online.
bot.run(bot_token)
    

"""
1-) Check if the alive_ones array is empty or not in play_round()
2-) Hide Bot Token --> line 11
3-) Make it online 7/24 and try/kill snippet from Berke.
4-) 
5-) 
6-) 
7-) 
8-) 
9-) choose 5 ppl ever round and make round count according to player count
10-) 
"""