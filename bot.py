import time
import requests
from fake_useragent import UserAgent
from datetime import datetime
from web3 import Web3
from eth_account.messages import encode_defunct
from loguru import logger
import json

class gokit_bot(object):
    def __init__(self,address,private_key,proxy=None):
        self.address = address
        self.private_key = private_key
        self.proxy = proxy
        user_agent = UserAgent()
        userAgent = user_agent.random
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-length': '35',
            'content-type': 'application/json',
            'origin': 'https://testnet.gokite.ai',
            'priority': 'u=1, i',
            'referer': 'https://testnet.gokite.ai/',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': userAgent
        }
        rpc = 'https://mainnet.infura.io/v3/60a69055106440c1b880b64075f46812'
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.session = requests.sessions.session()


    #发送request请求
    def send_request(self, method, url, headers=None, params=None, data=None, json_data=None, timeout=10, retries=3, delay=1):
        attempt = 0
        while attempt < retries:
            try:
                # 发送请求
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=timeout,
                    proxies=self.proxy
                )
                response.raise_for_status()  # 如果返回的HTTP状态码不是200，将抛出异常
                try:
                    return response.json()  # 尝试将响应转换为JSON
                except ValueError:  # 如果响应不是有效的JSON
                    logger.error("response转换json失败")
                    return response
            except requests.exceptions.RequestException as e:  # 捕获requests的所有异常
                attempt += 1
                logger.error(f"Request failed (attempt {attempt}/{retries}). Error: {e}")
                if attempt < retries:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)  # 等待一段时间后再重试
                else:
                    logger.error("达到最大重试次数. Request failed.")
                    raise  # 达到最大重试次数后抛出异常

    #获取当前时间戳
    def get_timestamp(self):
        timestamp = datetime.now()
        iso_format = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return iso_format


    #连接钱包获取登陆token
    def connect_wallet(self):
        try:
            iso_format = self.get_timestamp()
            response = self.send_request(
                method="POST",
                url="https://api-kiteai.bonusblock.io/api/auth/get-auth-ticket",
                headers=self.headers,
                json_data={'nonce':f"{iso_format}"}
            )
            data = response
            message_text = data["payload"]
            encode_message = encode_defunct(text=message_text)
            # account = self.w3.eth.account.from_key(self.private_key)
            if not self.w3.is_connected():
                raise Exception("Failed to connect to Ethereum network")
            signed_message = self.w3.eth.account.sign_message(encode_message,self.private_key)
            signature = "0x"+signed_message.signature.hex()
            logger.info("登陆信息签名成功")
            sign = self.send_request(
                method='POST',
                url= 'https://api-kiteai.bonusblock.io/api/auth/eth',
                headers = self.headers,
                json_data = {
                    "blockchainName":"ethereum",
                    "nonce": f"{iso_format}",
                    "referralId": "optionalReferral",
                    "signedMessage" : f"{signature}"
                }
            )
            session_data = sign.get("payload", {}).get("session", {})
            wallet_token = session_data.get("token", "")
            self.headers["x-auth-token"] = wallet_token
            return session_data
        except Exception as e:
            print('connect error'+ f'{e}')
            return None


    #获取账号信息
    def get_state(self):
        timestamp = self.get_timestamp()
        response = self.send_request(
            method='GET',
            url='https://api-kiteai.bonusblock.io/api/kite-ai/get-status',
            headers= self.headers,
            json_data = {
                "nonce":timestamp
            }
        )
        logger.info(response.get("payload", {}).get("userXp",{}))


    #获取当前社交任务进度
    def mission_success(self):

        #注册100分任务
        response = self.send_request(
            method='GET',
            url='https://api-kiteai.bonusblock.io/api/kite-ai/missions',
            headers= self.headers,
            json_data={
                "now":self.get_timestamp()
            }
        )
        logger.info(response.get("payload",{}))

        #tutorial 50分任务
        mission1 = self.send_request(
            method='POST',
            url = 'https://api-kiteai.bonusblock.io/api/forward-link/go/kiteai-mission-tutorial-1',
            headers= self.headers,
            json_data={
                "now": self.get_timestamp()
            }
        )
        logger.info("tutorial-complete ：" + str(mission1.get("success",{})))




