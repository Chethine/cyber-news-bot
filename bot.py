import feedparser
import asyncio
import os
from datetime import datetime, timedelta, timezone
from time import mktime
from telegram import Bot

# --- CONFIGURATION ---
# We fetch these from GitHub Secrets (Environment Variables)
BOT_TOKEN = os.environ.get("8224125570:AAGA5oCpuWDGXj4WHJExdQCdTyYW8lv9TC0")
CHANNEL_ID = os.environ.get("-1003703695791")

FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://aws.amazon.com/blogs/security/feed/"
]

async def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ Error: Missing BOT_TOKEN or CHANNEL_ID environment variables.")
        return

    bot = Bot(token=BOT_TOKEN)
    print("🔍 Scanning feeds for news from the last hour...")

    # Define the time window (last 65 mins to be safe for hourly runs)
    # We use UTC because most RSS feeds publish in GMT/UTC
    time_threshold = datetime.now(timezone.utc) - timedelta(minutes=65)

    for rss_url in FEEDS:
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries:
                # 1. Get the publication time
                if hasattr(entry, 'published_parsed'):
                    pub_time = datetime.fromtimestamp(mktime(entry.published_parsed), timezone.utc)
                elif hasattr(entry, 'updated_parsed'):
                     pub_time = datetime.fromtimestamp(mktime(entry.updated_parsed), timezone.utc)
                else:
                    continue # Skip if no date found

                # 2. Check if it is new (newer than our threshold)
                if pub_time > time_threshold:
                    print(f"found new: {entry.title}")
                    
                    msg = f"<b>{entry.title}</b>\n\n{entry.link}"
                    try:
                        await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='HTML')
                        await asyncio.sleep(1) 
                    except Exception as e:
                        print(f"Error sending: {e}")

        except Exception as e:
            print(f"Error parsing feed {rss_url}: {e}")

if __name__ == "__main__":
    asyncio.run(main())