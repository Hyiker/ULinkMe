import sys
from .config import dispatch_config_from_file, generate_default_config


def cli(args=None):
    if not args:
        args = sys.argv[1:]
    config = (
        dispatch_config_from_file(args[0])
        if len(args) >= 1
        else generate_default_config()
    )
    config.init_logging()
    config.init_observer()
    config.loop(1)
