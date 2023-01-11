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

pst_tz = pytz.timezone('America/Los_Angeles')


def get_days_missed(days_posted):
    dates = [datetime.strptime(key, DATE_FORMAT) for key in days_posted]
    min_date, max_date = min(dates), max(dates)
    return [(max_date - min_date).days + 1 - len(days_posted),
            min_date.strftime(DATE_FORMAT),
            max_date.strftime(DATE_FORMAT)]


def format_days_posted_result(days_posted):
    def get_formatted_content(content):
        if len(content) > MESSAGE_CHAR_LIMIT:
            return content[:MESSAGE_CHAR_LIMIT] + "..."
        return content

    res = []
    for key in days_posted:
        res.append((key, get_formatted_content(days_posted[key].content)))
    days_missed, min_date, max_date = get_days_missed(days_posted)
    return "Successful posts: {}, Date range considered: {}, Days missed: {}, Success samples: {}".format(
        len(days_posted), (min_date, max_date), days_missed,
        ["{}: {}".format(a, b) for a, b in res[:MESSAGE_LIMIT]])


def is_weekend(date):
    if date.weekday() < 5:
        return False
    else:  # 5 Sat, 6 Sun
        return True


def validate_date(date):
    if date.year != 2023:
        return False
    if is_weekend(date):
        return 9 <= date.hour <= 13
    return 9 <= date.hour <= 11


async def fetch_messages_for_channel(channel, limit):
    messages = channel.history(limit=limit)
    return [x async for x in messages]


async def handle_command(message):
    challenge_channel = client.get_channel(CHALLENGE_CHANNEL_ID)
    messages = await fetch_messages_for_channel(challenge_channel, 2000)
    bot_channel = client.get_channel(784787690281107517)
    messages = list(
        filter(
            lambda m: m.author.id == 164885252932632577 and validate_date(
                m.created_at.replace(tzinfo=timezone.utc).astimezone(tz=pst_tz)
            ), messages))
    days_posted = {}
    for x in messages:
        post_time = x.created_at.replace(tzinfo=timezone.utc).astimezone(
            tz=pst_tz)
        days_posted[(post_time.strftime(DATE_FORMAT))] = x
    result = format_days_posted_result(days_posted)
    print(result)
    await bot_channel.send(result)


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
