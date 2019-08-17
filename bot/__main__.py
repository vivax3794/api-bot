import logging
import traceback
from os import listdir
from os.path import isfile, join
from bot import constants
from discord.ext import commands

log = logging.getLogger(__name__)
log.setLevel(0)

bot = commands.Bot(command_prefix=constants.prefix)

if __name__ == "__main__":

    cogs_dir = "cogs"

    for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
        try:
            bot.load_extension(cogs_dir + "." + extension)
            log.critical(f"loaded {extension}")
        except Exception:
            log.error(f'Failed to load extension {extension}.')
            traceback.print_exc()
    log.critical("done")

    bot.run(constants.bot_token)