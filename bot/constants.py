from os import environ
from logging import getLogger

log = getLogger(__name__)

prefix = environ.get("prefix", ".")
bot_token = environ.get("bot_token")
if bot_token is None:
    log.critical("bot token missing")


tracker_token = environ.get("tracker_token")
if tracker_token is None:
    log.warning("tracker token missing")