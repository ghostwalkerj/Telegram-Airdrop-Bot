import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Enable / disable the airdrop
airdrop_live = True

# Enable / disable captcha
captcha = True

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
    "start_1": "Hi {} and welcome to our Airdrop!\n\nGet started by clicking the button below.\n\n",
    "start_2": "Hi {},\n\nYour address has been added to the airdrop list!\n\n",
    "start_captcha": "Hi {},\n\n",
    "airdrop_start": "The airdrop didn't start yet.",
    "airdrop_address": "Type in your address:",
    "airdrop_max_cap": "ℹ️ The airdrop reached its max cap.",
    "airdrop_walletused": "⚠️ That address has already been used. Use a different one.",
    "airdrop_confirmation": "✅ Your address has been added to airdrop list.",
    "airdrop_wallet_update": "✅ Your address has been updated.",
}
