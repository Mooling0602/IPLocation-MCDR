import json
import re
import requests

from mcdreforged.api.all import *

psi = ServerInterface.psi()
try:
    from matrix_sync.reporter import sender # type: ignore
    # 如果导入成功，则同时执行 sender 和 psi.broadcast
    send = lambda *args, **kwargs: (sender(*args, **kwargs), psi.broadcast(*args, **kwargs))
except ModuleNotFoundError:
    # 如果导入失败，则仅执行 psi.broadcast
    send = lambda *args, **kwargs: psi.broadcast(*args, **kwargs)

default_config = {
    "retry": 3
}

def on_load(server: PluginServerInterface, old):
    global config
    config = server.load_config_simple("config.json", default_config)

## 淘宝api接口
def getIPLoc(ip):
    url = "http://ip.taobao.com/outGetIpInfo?ip={}&accessKey=alibaba-inc".format(ip)
    try:
        req = requests.get(url).text
        IPLoc = json.loads(req)
        return IPLoc
    except json.JSONDecodeError:
        psi.logger.info("JSON解析错误，无法获取IP地址信息")
        return None
    except Exception as e:
        psi.logger.info(f"发生错误: {e}")
        return None

## 执行查询
def queryIPLoc(ip):
    retries = config["retry"]  ## 最大重试次数
    for attempt in range(retries):
        iploc = getIPLoc(ip)
        if iploc and iploc.get("code") == 0:
            ## 正确获取了IP信息时，进行处理
            country = iploc["data"]["country"]
            province = iploc["data"]["region"]
            city = iploc["data"]["city"]
            ## 若在国内，则隐藏国家信息
            if country == "中国":
                return "{}省{}市".format(province, city)  ## 国内显示省市信息
            else:
                return "{}{}{}".format(country, province, city)  ## 不在国内，显示原始信息
        else:
            psi.logger.info(f"尝试 {attempt + 1}/{retries} 获取IP信息失败，重试...")
    return "无法获取IP归属地"

## 处理玩家加入事件
def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    server.logger.info(f"正在查询玩家{player}的IP归属地...")
    ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    match = re.search(ip_pattern, info.content)
    if match:
        ip = match.group(0)  ## 提取出IP地址
        iploc = queryIPLoc(ip)
        send(f"[!] 玩家 {player} 的IP归属地：{iploc}")
    else:
        send(f"[!] 无法提取玩家 {player} 的IP地址")