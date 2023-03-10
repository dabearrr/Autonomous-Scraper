import os
from keep_alive import keep_alive
from datetime import datetime, timezone
import discord
import pytz

# constants
BOT_CHANNEL_ID = 784787690281107517
CHALLENGE_CHANNEL_ID = 1061190522045214751
MESSAGE_CHAR_LIMIT = 20
MESSAGE_LIMIT = 10
DATE_FORMAT = '%m/%d/%Y'
EMBED_TITLE = 'JON CHALLENGE'
EMBED_COLOR = 0xb70004
BOBAS_GIVEN = 0
pst_tz = pytz.timezone('America/Los_Angeles')
IMAGE_URL = "https://cdn.discordapp.com/attachments/163845730417639424/1063334341083680808/smiley-face-thumbs-up-thank-you-clipart-panda-free-clipart-images-4eZHzt-clipart.jpeg"
FAIL_IMAGE = "https://cdn.discordapp.com/attachments/163845730417639424/1063335681369313300/sad_emoji_meme.jpg"

# Gets number of days which were not successfully posted on.
# Assumes max_date is the newest successful post date (not accurate)
# Also returns the min date and max date of the date range considered
def get_days_missed(days_posted):
	dates = [datetime.strptime(key, DATE_FORMAT) for key in days_posted]
	min_date, max_date = min(dates), max(dates)
	return [(max_date - min_date).days + 1 - len(days_posted),
	        min_date.strftime(DATE_FORMAT),
	        max_date.strftime(DATE_FORMAT)]


# formats the message_content for successful posts to limit them to MESSAGE_CHAR_LIMIT characters
def get_formatted_content(content):
	if len(content) > MESSAGE_CHAR_LIMIT:
		return content[:MESSAGE_CHAR_LIMIT] + "..."
	return content


# formats bot message output
# embeds are special discord messages which can have fancy formatting
# https://cog-creators.github.io/discord-embed-sandbox/
def get_formatted_messsage_embed(days_posted):
	res = []
	for key in days_posted:
		res.append((key, get_formatted_content(days_posted[key].content)))
	days_missed, min_date, max_date = get_days_missed(days_posted)
	success_samples = ["{}: {}".format(a, b) for a, b in res[:MESSAGE_LIMIT]]
	embed = discord.Embed(title=EMBED_TITLE,
	                      description=EMBED_TITLE,
	                      color=EMBED_COLOR)
	embed.add_field(name='Successful posts',
	                value=len(days_posted),
	                inline=False)
	embed.add_field(name='Date range considered',
	                value='{} -> {}'.format(min_date, max_date),
	                inline=True)
	embed.add_field(name='Days missed',
	                value='None!' if days_missed == 0 else days_missed,
	                inline=True)
	embed.add_field(name='Success samples', value=success_samples, inline=True)
	embed.set_image(url=FAIL_IMAGE if days_missed > BOBAS_GIVEN else IMAGE_URL)
	return embed


def is_weekend(date):
	if date.weekday() < 5:
		return False
	else:  # 5 Sat, 6 Sun
		return True


# Checking if this datetime object is within a successful time-period
# For weekdays: [9am - 12pm)
# For weekends: [9am - 2pm)
def validate_successful_post_date(date):
	if date.year != 2023:
		return False
	if is_weekend(date):
		return 9 <= date.hour <= 13
	return 9 <= date.hour <= 11


async def fetch_messages_for_channel(channel, limit):
	messages = channel.history(limit=limit)
	return [x async for x in messages]


# Gets Map of date strings to a successful post on that date
def get_days_posted(channel_message_history):
	successful_posts = list(
	    filter(
	        lambda m: m.author.id == 164885252932632577 and
	        validate_successful_post_date(
	            m.created_at.replace(tzinfo=timezone.utc).astimezone(tz=pst_tz)
	        ), channel_message_history))
	days_posted = {}
	for x in successful_posts:
		post_time = x.created_at.replace(tzinfo=timezone.utc).astimezone(
		    tz=pst_tz)
		days_posted[(post_time.strftime(DATE_FORMAT))] = x
	return days_posted


async def handle_command(message):
	challenge_channel = client.get_channel(CHALLENGE_CHANNEL_ID)
	days_posted = get_days_posted(await fetch_messages_for_channel(
	    challenge_channel, 2000))
	bot_channel = client.get_channel(784787690281107517)
	embed_message = get_formatted_messsage_embed(days_posted)
	await bot_channel.send(embed=embed_message)


class MyClient(discord.Client):
	async def on_ready(self):
		print(f'Logged on as {self.user}!')

	async def on_message(self, message):
		print(f'Message from {message.author}: {message.content}')
		if message.content == "$$count":
			await handle_command(message)


# Request discord permissions to read message content + defaults
intents = discord.Intents.default()
intents.message_content = True

# Special replit command used to keep this running indefinitely
keep_alive()

# fetch auth token + start bot client
token = os.environ.get("DISCORD_BOT_SECRET")
client = MyClient(intents=intents)
client.run(token)
