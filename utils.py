import random

class DataProviderFromFile:
    def __init__(self, file_path: str):
        """初始化类，从文件读取数据"""
        self.file_path = file_path
        self._load_data()
        self.used_data = set()  # 用来记录已使用过的数据

    def _load_data(self):
        """从文件中读取数据"""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            # 读取所有行，并去掉每行的换行符
            self.data = [line.strip() for line in file.readlines()]

        if not self.data:
            raise ValueError("文件中没有数据")

    def get_data(self):
        """获取一条未使用过的数据"""
        # 随机打乱数据顺序，避免每次按顺序返回
        random.shuffle(self.data)

        for item in self.data:
            if item not in self.used_data:
                self.used_data.add(item)
                return item

        raise ValueError("没有未使用的数据了")