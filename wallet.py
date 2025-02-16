from eth_account import Account
from loguru import logger

class EthereumWallet:
    def __init__(self, filename="wallets.txt"):
        self.filename = filename

    def generate_wallet(self):
        # 生成新钱包
        account = Account.create()

        # 获取地址和私钥
        address = account.address

        private_key = account.key.hex()

        logger.info(f"生成钱包地址为：{address},私钥为：{private_key}")
        return {
            "address": address,
            "private_key": private_key
        }

    def save_wallet(self, data,code):
        # 追加模式打开文件并存储新钱包数据
        wallet_data = str(data["address"]+","+data["private_key"]+","+code["ref_code"])
        with open(self.filename, "a") as file:
            file.write(wallet_data + "\n")
        logger.info(f"Wallet data saved to {self.filename}")

if __name__ == '__main__':
    eth = EthereumWallet()
    wallet = eth.generate_wallet()
    print(wallet)