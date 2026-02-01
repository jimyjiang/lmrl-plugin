from .Common import Command
from .Common.Consts import LMRL_BIBLE_SEARCH_CMD


def SearchBible(query):
    cmd = "%s \"%s\"" % (LMRL_BIBLE_SEARCH_CMD.fget(), query)
    print(cmd)
    return Command.run_command(cmd)