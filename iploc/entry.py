from importlib import import_module

from mcdreforged.api.all import *
from iploc.config import config

psi = ServerInterface.psi()
try:
    from matrix_sync.reporter import sender # type: ignore
    # 同时转发到Matrix，若检测到插件MatrixSync正常工作
    send = lambda *args, **kwargs: (sender(*args, **kwargs), psi.broadcast(*args, **kwargs))
except ModuleNotFoundError:
    # 没有检测到MatrixSync，仅进行广播
    send = lambda *args, **kwargs: psi.broadcast(*args, **kwargs)
except ImportError:
    # 无法导入MatrixSync的API，判断为2.4.0新版本，导入修改后的新接口名称
    from matrix_sync.reporter import send_matrix # type: ignore
    send = lambda *args, **kwargs: (send_matrix(*args, **kwargs), psi.broadcast(*args, **kwargs))

def on_load(server: PluginServerInterface, old):
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
        send(f"[!] 玩家 {player} 的IP归属地：{location}")
    except ModuleNotFoundError:
        server.logger.error(f"不支持该API接口: {using_api}，请正确配置插件（使用taobao或baidu）！")