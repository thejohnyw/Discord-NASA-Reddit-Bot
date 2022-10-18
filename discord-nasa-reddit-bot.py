'''
Author: John Wang
October 2022
Purpose: Discord Bot that sends NASA pictures and posts them to Reddit upon mention!
'''
import discord #Discord API
import os
import random
from dotenv import load_dotenv
import requests
from datetime import date
import praw #Reddit API wrapper

#os and dotenv are used to privately access password and API keys
load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
nasa_key = os.getenv('NASA_KEY')
reddit_client = os.getenv('REDDIT_CLIENT')
reddit_secret = os.getenv('REDDIT_SECRET')
reddit_pass = os.getenv('REDDIT_PASS')



#function to post pic to subreddit APOD: https://www.reddit.com/r/apod/, and comment description under the post
def POST(description, pic):
    post = reddit.subreddit('apod').submit('User Generated APOD', url=pic)
    post.reply(body = description)

#connects with Reddit API
reddit = praw.Reddit(client_id = reddit_client, client_secret = reddit_secret,
    user_agent = 'nasa-discord bot', username = 'nasadiscordredditbot', password = reddit_pass, check_for_async = False)

posts = [] #temporary memory of what discord bot sends so that it can post the most recent one to reddit



#generate a random date for NASA Astronomy pic
def randomdate():
    month, year = random.randint(1,12), random.randint(1996,2021)
    days_in_month = {1:31, 2:28, 3:31, 4:29, 5:31, 6:30, 7:29, 8:31, 9:30, 10:31, 11:30, 12:30}
    if (year%4 == 0 and year%100 != 0) or (year%400 == 0): #leap year consideration
        days_in_month[2] = 29
    day = random.randint(1,days_in_month[month])
    date = str(year)+'-'+str(month)+'-'+str(day)
    return date

#calls NASA API for picture on given date; returns HD picture and its description 
def nasa_info(option, t_date=None): #parameters: option is what date you want: a random one, specific one, or today's date
    #--> t_date is optional parameter, used for specific date
    options_dict = {'random': randomdate(), 'specific': t_date, 'today': date.today()}
    given_date = options_dict[option]
    call = 'https://api.nasa.gov/planetary/apod?date={}&hd=True&api_key={}'.format(given_date, nasa_key) #NASA APOD API
    r = requests.get(call)
    return r.json()["explanation"], \
        r.json()["hdurl"] 



#creates client to connect with Discord API
#using all intents because accessing user message contents requires it
client = discord.Client(intents=discord.Intents.all()) 

botID = '<@1030953607073378415>' #allows for users to mention bot using @

#event when bot ready: print to console that it's ready
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

#event for when new member joins a server that is using the bot: it sends a dm about possible bot commands
@client.event
async def on_member_join(member):
    await member.send(
        'Welcome! I am NASA/Reddit Bot! To use my commands, mention me then type the command as shown. \n' +
        'For a random Astronomy picture and description, "@nasa_bot random" \n' +
        'For the picture of the day, "@nasa_bot today" \n' +
        'For a specific date, "@nasa_bot date: year-month-day" \n' +
        'If you really like the APOD, post it to reddit using "@nasa_bot post"'
    )

#event for user sending a message/command
@client.event
async def on_message(message): #parameter: user's message

    if message.author == client.user or not message.content.startswith(botID): #checks for user message and makes sure discord bot won't message unless it is mentioned
        return

    if message.content == botID + " random":
        descript, pic = nasa_info('random')
        
    elif message.content == botID + " today":
        descript, pic = nasa_info('today')
        
    elif message.content.startswith(botID + " date: "):
        spec_date = message.content[len(botID)+7:] #date is value after " date: " (7 characters); ex: yyyy-mm-dd
        if int(spec_date[:4]) not in range(1996,2022): #check if valid year
            await message.channel.send('invalid date')
            return
        descript, pic = nasa_info('specific', t_date=spec_date) #takes t_date parameter as user input of date

    elif message.content == botID + " post":
        if posts:
            POST(posts[-2], posts[-1]) #post most recent nasa message/pic from bot to Reddit
            await message.channel.send('Successfully posted to reddit!! View here: https://www.reddit.com/user/nasadiscordredditbot')
            return
        else: #if user tries to post, but there's no bot-generated NASA APOD yet
            await message.channel.send('Error: No previous APOD to post')
            return
    
    else: #if user mentions bot but doesn't give any of above commands
        await message.channel.send('Invalid command: command not found')
        return
        
    bot_reply = descript + "\n\n{}\n\n*".format(pic)
    posts.append(bot_reply) #appends bot's NASA pics/messages to posts list
    posts.append(pic)
    await message.channel.send(bot_reply)
    
        
client.run(discord_token)