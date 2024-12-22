import requests
import re

from mcdreforged.api.all import *
from iploc.config import config

# 百度API接口
def getIPLoc(server: ServerInterface, ip: str):
    url = f"https://opendata.baidu.com/api.php?co=&resource_id=6006&oe=utf8&query={ip}"
    retries = config.get("retry", 3)  # 从配置文件中获取重试次数，默认为 3
    for attempt in range(retries):
        try:
            # 发送请求
            response = requests.get(url)
            response.raise_for_status()  # 如果响应返回非 2xx 状态码，会抛出异常
            # 解析返回的 JSON 数据
            data = response.json()

            # 检查返回的状态是否为成功
            if data["status"] == "0":
                # 提取 IP 归属地信息
                if data["data"] != []:
                    location = data["data"][0]["location"]
                    return location
                else:
                    pattern = r"^127\.(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])){2}$"
                    if re.fullmatch(pattern, ip):
                        location = "本地回环地址"
                        return location
                    else:
                        return "似乎为无效或非法IP地址，无法获取其归属地！"
            else:
                return "无法获取IP归属地"
        except requests.RequestException as e:
            if attempt < retries - 1:
                server.logger.warning(f"尝试获取IP归属地失败: {e}，正在重试 ({attempt + 1}/{retries})...")
            else:
                server.logger.warning(f"API请求错误: {e}")
                return "无法获取IP归属地"