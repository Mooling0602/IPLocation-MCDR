from mcdreforged.api.all import *

psi = ServerInterface.psi()

default_config = {
    "api": "baidu",
    "retry": 3,
    "format": "[!] 玩家 %player% 的IP归属地：%location%"
}

config = psi.load_config_simple("config.json", default_config)