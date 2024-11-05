import json
import requests

from mcdreforged.api.all import *
from iploc.config import config

psi = ServerInterface.psi()

## 淘宝api接口
def getIPLoc(ip):
    url = "https://ip.taobao.com/outGetIpInfo?ip={}&accessKey=alibaba-inc".format(ip)
    req = requests.get(url).text
    IPLoc = json.loads(req)
    retries = config["retry"]  ## 最大重试次数
    for attempt in range(retries):
        if IPLoc and IPLoc.get("code") == 0:
            ## 正确获取了IP信息时，进行处理
            country = IPLoc["data"]["country"]
            province = IPLoc["data"]["region"]
            city = IPLoc["data"]["city"]
            isp = IPLoc["data"]["isp"]
            ## 若在国内，则隐藏国家信息
            if country == "中国":
                return "{}省{}市 {}".format(province, city, isp)  ## 国内显示省市信息
            else:
                return "{}{}{} {}".format(country, province, city, isp)  ## 不在国内，显示原始信息
        else:
            psi.logger.info(f"尝试 {attempt + 1}/{retries} 获取IP信息失败，重试...")
    return "无法获取IP归属地"