from pony.orm import *

db = Database()


class User(db.Entity):
    telegram_handle = Required(str, unique=True)
    telegram_id = Required(int, unique=True)
    address = Optional(str, unique=True)
    email = Optional(str)
    twitter = Optional(str)
    twitter_follow = Required(bool, default=False, sql_default='0')
    twitter_retweet = Required(bool, default=False, sql_default='0')
    quized_passed = Required(bool, default=False, sql_default='0')
    airdrop_user = Required(bool, default=False, sql_default='0')
