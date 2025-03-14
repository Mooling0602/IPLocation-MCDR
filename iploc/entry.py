from importlib import import_module
from mcdreforged.api.all import *
from iploc.config import config

psi = ServerInterface.psi()
try:
    # MatrixSync v2.5.0+
    from matrix_sync.commands import matrix_reporter
    send = lambda *args, **kwargs: (matrix_reporter(*args, **kwargs), psi.broadcast(*args, **kwargs))
except ModuleNotFoundError:
    # 没有检测到MatrixSync，仅进行广播
    send = lambda *args, **kwargs: psi.broadcast(*args, **kwargs)

def on_load(server: PluginServerInterface, prev_module):
    server.register_event_listener('player_ip_logger.player_login', on_player_ip_logged)


# 调用Player IP Logger
@new_thread('IPLoc-Query')
def on_player_ip_logged(server: PluginServerInterface, player_name:str, player_ip:str):
    player = player_name
    server.logger.info(f"正在查询玩家{player}的IP归属地...")
    ip = player_ip
    using_api: str = config["api"]
    api_module = import_module(f"iploc.api.{using_api}")
    try:
        location = api_module.getIPLoc(server, ip)
        message = config["format"].replace('%player%', player).replace('%location%', location)
        send(message)
    except ModuleNotFoundError:
        server.logger.error(f"不支持该API接口: {using_api}，请正确配置插件（使用taobao或baidu）！")
