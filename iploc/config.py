from mcdreforged.api.all import *

psi = ServerInterface.psi()

default_config = {
    "api": "baidu",
    "retry": 3
}

def load_config():
    global config
    config = psi.load_config_simple("config.json", default_config)