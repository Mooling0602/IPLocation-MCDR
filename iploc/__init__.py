import json
import re
import requests
## 为基本注释

# 代码部分为对接MatrixSync插件的部分，可取消注释后使用，正常情况无需修改，也可以删除
# import asyncio
# import matrix_sync.client

from mcdreforged.api.all import *
from matrix_sync.reporter import sendMsg

psi = ServerInterface.psi()
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
        server.broadcast(f"[!] 玩家 {player} 的IP归属地：{iploc}")
        # asyncio.run(sendMsg(f"[!] 玩家 {player} 的IP归属地：{iploc}"))
    else:
        server.broadcast(f"[!] 无法提取玩家 {player} 的IP地址")
        # asyncio.run(sendMsg(f"[!] 无法提取玩家 {player} 的IP地址"))
