import iploc.api

from mcdreforged.api.all import *
from iploc.config import load_config

psi = ServerInterface.psi()
try:
    from matrix_sync.reporter import sender # type: ignore
    # 同时转发到Matrix，若检测到插件MatrixSync正常工作
    send = lambda *args, **kwargs: (sender(*args, **kwargs), psi.broadcast(*args, **kwargs))
except ModuleNotFoundError:
    # 没有检测到MatrixSync，仅进行广播
    send = lambda *args, **kwargs: psi.broadcast(*args, **kwargs)

def on_load(server: PluginServerInterface, old):
    load_config()
    server.register_event_listener('player_ip_logger.player_login', on_player_ip_logged)


# 调用Player IP Logger
def on_player_ip_logged(server: PluginServerInterface, player_name:str, player_ip:str):
    player = player_name
    server.logger.info(f"正在查询玩家{player}的IP归属地...")
    ip = player_ip
    using_api: str = iploc.config.api
    location = getattr(iploc.api, using_api)(ip)
    send(f"[!] 玩家 {player} 的IP归属地：{location}")

# 旧版检测方式，在玩家上线时解析其IP，若上面调用的插件工作稳定，此部分将在后续版本彻底移除
# def on_player_joined(server: PluginServerInterface, player: str, info: Info):
#     server.logger.info(f"正在查询玩家{player}的IP归属地...")
#     ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
#     match = re.search(ip_pattern, info.content)
#     if match:
#         ip = match.group(0)  ## 提取出IP地址
#         using_api = iploc.config.api
#         iploc = getattr(iploc.api, using_api)(ip)
#         send(f"[!] 玩家 {player} 的IP归属地：{iploc}")
#     else:
#         send(f"[!] 无法提取玩家 {player} 的IP地址")