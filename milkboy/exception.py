# ユーザー定義例外クラス
class NoResultException(Exception):
    """
        検索結果が0件だった場合の例外
    """
    def __init__(self, target):
        self.target = target

    def __str__(self):
        return f"{self.target}が見つかりませんでした"


class ResultNoneException(Exception):
    """
        実行結果がNoneだった場合の例外
    """
    def __init__(self, target):
        self.target = target

    def __str__(self):
        return f"{self.target}がNoneです"


class FailError(Exception):
    """
        ネタの生成に失敗した場合のエラー
    """
    def __init__(self, target):
        self.target = target

    def __str__(self):
        return f"{self.target}に失敗しました"


class InvalidSentenceException(Exception):
    """
        抽出した文章がネタに使うには不適切だった場合のエラー
    """
    def __init__(self, reason, sentence):
        self.reason = reason
        self.sentence = sentence

    def __str__(self):
        return f"{self.reason}ため、条件を満たさない文章です:{self.sentence}"


class EmptySentenceException(Exception):
    """
        抽出した文章が空だった場合のエラー
    """
    def __init__(self):
        pass

    def __str__(self):
        return "文章が空です"
