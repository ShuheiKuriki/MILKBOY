# ユーザー定義例外クラス
class NoResultException(Exception):
    def __init__(self, target):
        self.target = target

    def __str__(self):
        return f"{self.target}が見つかりませんでした"


class ResultNoneException(Exception):
    def __init__(self, target):
        self.target = target

    def __str__(self):
        return f"{self.target}がNoneです"
