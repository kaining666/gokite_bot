from bot import gokit_bot
from bot_proxy import ProxyChecker
from wallet import EthereumWallet

def run():
    wallet_manager = EthereumWallet()
    wallet_data = wallet_manager.generate_wallet()
    checker = ProxyChecker()
    try:
        proxy = checker.get_unique_proxy()
        bot = gokit_bot(private_key=wallet_data["private_key"], proxy=proxy)
        bot.connect_wallet()
        bot.mission_success()
        bot.get_state()
        wallet_manager.save_wallet(wallet_data)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    run()