import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Enable / disable the airdrop
airdrop_live = True

# Telegram
api_token = os.environ.get("API_TOKEN")

host = os.environ.get("HOST")  # ip/host where the bot is running

log_channel = -12351238734976  # Channel ID. Example: -1001355597767
# Telegram User ID's. Admins are able to execute command "/airdroplist"
admins = os.environ.get("ADMIN_LIST").split(",")
airdrop_cap = 100  # Max airdrop submissions that are being accepted
wallet_changes = 3  # How often a user is allowed to change their wallet address

# MySQL Database
mysql_host = "localhost"
mysql_db = "TelegramAirdropBot"
mysql_user = os.environ.get("MYSQL_USER")
mysql_pw = os.environ.get("MYSQL_PW")

texts = {
    "start_1": "Hi {} and welcome!\n\nEstate Protocol is airdropping $30,000 worth of tokens to our participants.\n\n Please follow all the rules to be eligible.",
    "start_2": "Hi {},\n\nYour address has been added to the airdrop list!\n\n",
    "agree": "Do you agree to take full legal responsibility according to your local laws for participating in this airdrop?",
    "email": "What is your email address?",
    "bad_email": "Please try again with a valid email address.",
    "twitter_handle": "What is your Twitter handle?",
    "follow_twitter": "Please follow Estate Protocol on Twitter and retweet the pinned post.",
    "telegram": "Also join our Telegram community: ",
    "whitepaper": "Lastly read our whitepaper, it’s an easy to read document detailing our current and future plans. It can be found on xx. Type 'ok' to take the whitepaper quiz.",
    "airdrop_start": "The airdrop didn't start yet.",
    "airdrop_address": "What’s your BSC address? Please make sure not to give an exchange address: ",
    "airdrop_max_cap": "ℹ️ The airdrop reached its max cap.",
    "airdrop_walletused": "⚠️ That address has already been used. Use a different one.",
    "airdrop_confirmation": "✅ Your address has been added to airdrop list.\n\n Keep an eye out on our Twitter account and Telegram community for the announcements of the results!",
    "airdrop_wallet_update": "✅ Your address has been updated.",
    "quiz": "",
    "survey": ""
}
