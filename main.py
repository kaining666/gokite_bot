from bot import gokit_bot
from bot_proxy import ProxyChecker
from utils import DataProviderFromFile
from wallet import EthereumWallet
from xAuth import XAuth
import os

xfile = os.path.abspath('twitter_token.txt')

def register():
    wallet_manager = EthereumWallet()
    wallet_data = wallet_manager.generate_wallet()
    checker = ProxyChecker()
    provider = DataProviderFromFile(xfile)
    while True:
        try:
            proxy = checker.get_unique_proxy()
            twitter_token = provider.get_data()
            xauth = XAuth(auth_token=twitter_token,proxy=proxy)
            bot = gokit_bot(address=wallet_data["address"],private_key=wallet_data["private_key"], proxy=proxy)
            bot.connect_wallet()
            #50分
            bot.mission_success()

            #电报任务
            bot.tel_mission()

            #twitter验证
            oauth_token = bot.social_link('twitter')
            verifier = xauth.oauth1(oauth_token)
            bot.submit_x_token(social='twitter',oauth_token=oauth_token,oauth_verifier=verifier)

            #保存地址，私钥，邀请码
            ref_code = bot.get_state()
            wallet_manager.save_wallet(wallet_data,ref_code)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    register()