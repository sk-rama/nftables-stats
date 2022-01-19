from functools import cache
from typing import Literal
from pydantic import BaseSettings


ruleset = {}

class Settings(BaseSettings):
    app_name: str = "Nftables Sherlog API"
    admin_email: str = "admin@email.com"
    items_per_user: int = 50
    ip_whitelist = ['127.0.0.1', '82.99.137.0/24', '84.244.68.0/24', '212.158.133.0/24']
    tags_metadata = [
        {
            'name': 'IP',
            'description': 'Operations with IP addresses. The **login** logic is also here.',
        },
    ]
    nft_families = Literal['inet', 'ip']
    nft_tables   = Literal['table_filter']
    nft_sets     = Literal['blackhole']
    nft_desc     = Literal['chile', 'kj', 'bookinfo']
    log_config = {
        "version":1,
        "root":{
            "handlers" : ["file_handler", "console2"],
            "level": "DEBUG",
        },
        "loggers":{
            "file_logger":{
                "handlers" : ["file_handler"],
                "level": "INFO",
            }
        },
        "handlers":{
            "file_handler":{
                "formatter": "std_out1",
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "filename": "all_messages.log",
            },
            "console2":{
                "formatter": "std_out2",
                "class": "logging.StreamHandler",
                "level": "DEBUG",
            }
        },
        "formatters":{
            "std_out1": {
                "format": "%(asctime)s.%(msecs)03d : %(levelname)s : %(module)s : %(funcName)s : %(lineno)d : (Process Details : (%(process)d, %(processName)s), Thread Details : (%(thread)d, %(threadName)s))\nLog : %(message)s",
                "datefmt":"%d-%m-%Y %I:%M:%S"
            },
            "std_out2": {
                "format": "%(asctime)s.%(msecs)03d : %(levelname)s : %(name)s : %(funcName)s : %(message)s",
                "datefmt":"%d-%m-%Y %I:%M:%S"
            }
        },
    }

    description  = """
Sherlog Technology Nftables API 🚀

## IP

You will be able to:

* **Get IP** (_not implemented_).
* **Add IP to nftables** (_DONE - implemented_).
"""

def get_ruleset():
    global ruleset
    return ruleset

def set_ruleset(d: dict):
    global ruleset
    ruleset.clear()
    ruleset = {**d}


@cache
def get_settings():
    return Settings()
