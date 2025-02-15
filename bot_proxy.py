import requests
import random
from loguru import logger
class ProxyChecker:
    def __init__(self, proxy_file="proxy.txt", test_url="https://httpbin.org/ip", timeout=5):
        self.proxy_file = proxy_file
        self.test_url = test_url
        self.timeout = timeout
        self.used_proxies = set()
        self.proxies = self.load_proxies()

    def load_proxies(self):
        #从文件中读取代理列表，格式: username:password@ip:port
        with open(self.proxy_file, "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies

    def check_proxy(self, proxy):
        #检测代理是否可用
        proxy_dict = {"http": proxy, "https": proxy, "socks5": proxy} if proxy.startswith("socks") else {"http": proxy, "https": proxy}
        try:
            response = requests.get(self.test_url, proxies=proxy_dict, timeout=self.timeout)
            if response.status_code == 200:
                logger.info(f"{proxy} : 当前代理可用")
                return proxy_dict
        except requests.RequestException:
            logger.error(f"{proxy} : 当前代理不可用")
            pass
        return None


    def get_unique_proxy(self):
        #随机选择并验证一条未使用的代理
        available_proxies = [proxy for proxy in self.proxies if proxy not in self.used_proxies]
        if not available_proxies:
            logger.error("代理用光了")
            raise Exception("No more unique proxies available.")

        while available_proxies:
            proxy = random.choice(available_proxies)
            valid_proxy = self.check_proxy(proxy)
            if valid_proxy:
                self.used_proxies.add(proxy)
                return valid_proxy
            else:
                self.used_proxies.add(proxy)
                available_proxies.remove(proxy)

        raise Exception("No valid proxies found.")



