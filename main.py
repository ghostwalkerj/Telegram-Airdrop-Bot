import os
import ssl
import logging
from io import BytesIO
from time import gmtime, strftime

import eth_utils
import pymysql
import telebot
from aiohttp import web
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import config
from entity import User, db
from pony.orm import *
import util

logging.basicConfig(level=logging.DEBUG)
# Constants
WEBHOOK_HOST = config.host
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port needs to be 'open')
WEBHOOK_LISTEN = config.host

WEBHOOK_SSL_CERT = "./webhook_cert.pem"  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = "./webhook_pkey.pem"  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(config.api_token)


bot = telebot.TeleBot(config.api_token)
app = web.Application()

db.bind(provider='mysql', host=config.mysql_host,
        user=config.mysql_user, passwd=config.mysql_pw, db=config.mysql_db)
logging.debug("SQL Connected")
db.generate_mapping(create_tables=True)
logging.debug("Tables created")


@db_session
def get_airdrop_users():
    return User.select(lambda a: a.airdrop_user == True)


@db_session
def get_user(message):
    bot.send_chat_action(message.chat.id, "typing")
    user = User.get(telegram_handle=message.chat.id)
    if(user == None or user.airdrop_user == True):
        handle_start(message)
    else:
        logging.debug("Found user %s" % user.telegram_handle)
        return user


defaultkeyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True)
defaultkeyboard.row(types.KeyboardButton("🚀 Join Airdrop"))

airdropkeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
airdropkeyboard.row(types.KeyboardButton("💼 View Wallet Address"))


def cancel_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        "Cancel Operation", callback_data="cancel_input"))
    return markup


@bot.message_handler(
    func=lambda message: message.chat.type == "private", commands=["start"]
)
@db_session
def handle_start(message):
    bot.send_chat_action(message.chat.id, "typing")
    logging.debug("/start")
    user = None
    try:
        user = User.get(telegram_handle=message.chat.id)
    except Exception as e:
        logging.error(e)
    if user is None:
        user = User(telegram_handle=message.chat.id)
        logging.debug("User created")
    if user.airdrop_user is True:
        bot.send_message(
            message.chat.id,
            config.texts["start_2"].format(message.from_user.first_name),
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=airdropkeyboard,
        )
    elif not config.airdrop_live:
        bot.send_message(
            message.chat.id,
            config.texts["airdrop_start"],
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    elif get_airdrop_users().count() >= config.airdrop_cap:
        bot.send_message(
            message.chat.id,
            config.texts["airdrop_max_cap"],
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    else:
        bot.send_message(
            message.chat.id,
            config.texts["start_1"].format(message.from_user.first_name)
            + " [» Rules](https://estateprotocol.com/).",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=defaultkeyboard,
        )


@bot.message_handler(
    func=lambda message: message.chat.type == "private"
    and message.text == "🚀 Join Airdrop"
)
@db_session
def handle_join_airdrop(message):
    user = User(get_user(message))
    logging.debug("Joining Airdrop")
    bot.send_message(message.chat.id,
                     config.texts["agree"],
                     reply_markup=gen_yesno())


def gen_yesno():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"),
               InlineKeyboardButton("No", callback_data="cb_no"))
    return markup


@bot.message_handler(
    func=lambda message: message.chat.type == "private"
    and message.text == "💼 View Wallet Address"
)
@db_session
def handle_view_wallet(message):
    user = User(get_user(message))
    if user.airdrop_user == True:
        bot.send_message(
            message.chat.id,
            text="Your tokens will be sent to:\n\n[{0}](https://etherscan.io/address/{0})".format(
                user.address),
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=edit_wallet_address(message),
        )


@db_session
def address_check(message):
    user = User(get_user(message))
    if get_airdrop_users().count() >= config.airdrop_cap:
        bot.send_message(
            message.chat.id, config.texts["airdrop_max_cap"], parse_mode="Markdown"
        )
        bot.clear_step_handler(message)
    elif User.get(address=message.text):
        msg = bot.reply_to(
            message,
            config.texts["airdrop_walletused"],
            parse_mode="Markdown",
            reply_markup=cancel_button(),
        )
        bot.register_next_step_handler(msg, address_check)
    elif eth_utils.is_address(message.text):
        user.address = message.text
        try:
            bot.send_message(
                config.log_channel,
                "🎈 *#Airdrop_Entry ({0}):*\n"
                " • User: [{1}](tg://user?id={2}) (#id{2})\n"
                " • Address: [{3}](https://etherscan.io/address/{3})\n"
                " • Time: `{4} UTC`".format(
                    get_airdrop_users().count()),
                bot.get_chat(message.chat.id).first_name,
                message.chat.id,
                message.text,
                strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                parse_mode="Markdown",
                disable_web_page_preview=True)
        except:
            pass
        else:
            msg = bot.reply_to(
                message,
                "❌ Invalid $ETH address. Try again:",
                parse_mode="Markdown",
                reply_markup=cancel_button(),
            )
            bot.register_next_step_handler(msg, address_check)


@db_session
def address_check_update(message, old_address):
    user = User(get_user(message))
    if User.get(address=message.text):
        msg = bot.reply_to(
            message, config.texts["airdrop_walletused"], parse_mode="Markdown"
        )
        bot.register_next_step_handler(
            msg, address_check_update, old_address)
    elif eth_utils.is_address(message.text):
        user.address = message.text
        try:
            bot.send_message(
                config.log_channel,
                "📝 *#Address_Updated:*\n"
                " • User: [{1}](tg://user?id={2}) (#id{2})\n"
                " • Old Address: [{3}](https://etherscan.io/address/{3})\n"
                " • New Address: [{4}](https://etherscan.io/address/{4})\n"
                " • Time: `{5} UTC`".format(
                    get_airdrop_users().count(),
                    bot.get_chat(message.chat.id).first_name,
                    message.chat.id,
                    old_address,
                    message.text,
                    strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                ),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        except:
            pass
        else:
            msg = bot.reply_to(
                message,
                "❌ Invalid address. Try again:",
                parse_mode="Markdown",
                reply_markup=cancel_button(),
            )
            bot.register_next_step_handler(
                msg, address_check_update, old_address)


@ db_session
def verify_email(message):
    try:
        user = User(get_user(message))
        email = message.text
        logging.debug("Email received %s" % email)
        # Verify email here
        email_verified = util.check_email(email)
        if email_verified:
            user.email = email
            msg = bot.send_message(
                message.chat.id,
                config.texts["twitter_handle"],
                parse_mode="Markdown",
            )
            bot.register_next_step_handler(msg, verify_twitter)
        else:
            msg = bot.send_message(
                message.chat.id,
                config.texts["bad_email"],
                parse_mode="Markdown",
            )
            bot.register_next_step_handler(msg, verify_email)
    except Exception as e:
        logging.error(e)


@ db_session
def verify_twitter(message):
    try:
        user = User(get_user(message))
        twitter = message.text
        logging.debug("Twitter received %s" % twitter)
        user.twitter = twitter
        msg = bot.send_message(
            message.chat.id,
            config.texts["follow_twitter"],
            parse_mode="Markdown",
        )
        msg = bot.send_message(
            message.chat.id,
            config.texts["telegram"],
            parse_mode="Markdown",
        )
        msg = bot.send_message(
            message.chat.id,
            config.texts["whitepaper"],
            parse_mode="Markdown",
        )
        bot.register_next_step_handler(msg, quiz)

    except Exception as e:
        logging.error(e)


def quiz(message):
    try:
        msg = bot.send_message(
            message.chat.id,
            config.texts["whitepaper"],
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(e)


@bot.message_handler(
    func=lambda message: message.chat.id in config.admins, commands=["airdroplist"]
)
@db_session
def handle_text(message):
    bot.send_chat_action(message.chat.id, "upload_document")
    users = get_airdrop_users()
    airdrop = "AIRDROP ({}):\n\n".format(users.count())
    for user in users:
        if user.address is not None:
            address = user.address
            airdrop += "{}\n".format(address)

        with BytesIO(str.encode(airdrop)) as output:
            output.name = "AIRDROP.txt"
            bot.send_document(
                message.chat.id,
                output,
                caption="Here's the list with all airdrop addresses.",
            )
            return


@ bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        msg = bot.send_message(
            call.message.chat.id,
            config.texts["email"],
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
        bot.register_next_step_handler(msg, verify_email)
    elif call.data == "cb_no":
        msg = bot.send_message(
            call.message.chat.id,
            "😒 Whatever"
        )
        bot.register_next_step_handler(msg, "start")

    elif call.data == "cancel_input":
        bot.delete_message(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )
        if get_airdrop_users().count() >= config.airdrop_cap:
            bot.send_message(
                call.message.chat.id,
                "✅ Operation canceled.\n\nℹ️ The airdrop reached its max cap.",
            )
        elif User.get(address=call.message.text):
            bot.send_message(
                call.message.chat.id,
                "✅ Operation canceled.",
                reply_markup=airdropkeyboard,
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "✅ Operation canceled.",
                reply_markup=defaultkeyboard,
            )
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    elif call.data == "edit_wallet_address":
        user = User(get_user(call.message))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Please send your new address:",
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
        bot.register_next_step_handler(
            call.message, address_check_update, user.address
        )
    else:
        bot.answer_callback_query(
            call.id,
            "⚠️ You can't change your address anymore.",
            show_alert=True,
        )


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(
    url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, "r")
)

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Process webhook calls


async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)
app.router.add_post('/{token}/', handle)

# Start aiohttp server
web.run_app(
    app,
    host='0.0.0.0',
    port=WEBHOOK_PORT,
    ssl_context=context,
)
