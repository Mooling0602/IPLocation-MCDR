import requests

from mcdreforged.api.all import *
from iploc.config import config

psi = ServerInterface.psi()

# 百度API接口
@new_thread('IPLoc-API: Baidu')
def getIPLoc(ip):
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
                location = data["data"][0]["location"]
                return location
            else:
                return "无法获取IP归属地"
        except requests.RequestException as e:
            if attempt < retries - 1:
                psi.logger.info(f"尝试获取IP信息失败: {e}，正在重试 ({attempt + 1}/{retries})...")
            else:
                psi.logger.warning(f"请求错误: {e}")
                return "无法获取IP归属地"