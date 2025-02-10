import requests
from fake_useragent import UserAgent
from datetime import datetime
from web3 import Web3
from eth_account.messages import encode_defunct
from loguru import logger


class gokit_bot(object):
    def __init__(self,private_key,proxy=None):
        self.private_key = private_key
        self.proxy = proxy
        if proxy:
            self.proxies_conf = {
                "proxies": {
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}"
                }
            }
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
        self.w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs=self.proxy))
        self.session = requests.sessions.session()


    #发送request请求
    def send_request(self,method, url, headers=None, params=None, data=None, json_data=None, timeout=10):
        try:
            # 发送请求
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout
            )

            try:
                return response.json()
            except Exception as e:
                return response
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

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
        response = self.send_request(
            method='GET',
            url='https://api-kiteai.bonusblock.io/api/kite-ai/missions',
            headers= self.headers,
            json_data={
                "now":self.get_timestamp()
            }
        )
        logger.info(response.get("payload",{}))
if __name__ == '__main__':
    bot = gokit_bot(private_key='')
    bot.connect_wallet()
    bot.mission_success()
    bot.get_state()