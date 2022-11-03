import asyncio
import random
import re

import requests
from bs4 import BeautifulSoup

try:
    from .exception import ResultNoneException, InvalidSentenceException, EmptySentenceException
except ImportError:
    from exception import ResultNoneException, InvalidSentenceException, EmptySentenceException
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("ja_ginza")
matcher = Matcher(nlp.vocab)

# global
P_TAGS_MAX = 15
BASE_WIKI = 'https://ja.wikipedia.org/wiki'
RANDOM_WIKI = f'{BASE_WIKI}/Special:Random'


async def handler(loop, urls, func):
    """
        非同期処理のためにloop.run_until_completeに与えるコルーチンのリストを返す
    """
    async def async_ex(url):
        # 非同期処理１つ分のコルーチン
        async with asyncio.Semaphore(20):
            # セマフォで最大並列数を制限
            future = loop.run_in_executor(None, func, url)
            return await future

    return await asyncio.gather(*[async_ex(url) for url in urls])


def get_present_only(present, seed_num):
    """つかみだけのステージを取得"""
    return [
        {
            "input_theme": "",
            "theme": "",
            "stage": -1,
            "seed": seed_num,
            "next_is_last": True,
            "category": "",
            "anti_theme": "",
            "featX": "",
            "featX_reply": "",
            "anti_featX": "",
            "anti_featX_reply": "",
            "conjunction": "",
            "present": present
        }
    ]


def feat_to_script(feat, is_anti, theme):
    if len(feat) == 0 and not is_anti:
        speech = "オカンが言うには、これと言った特徴がないらしいねん。"
        reply = "これと言った特徴がない?! お前のオカン、頑張って特徴を思い出してくれ。"
    elif len(feat) == 0 and is_anti:
        speech = "オカン、それの特徴がもう思い出せないらしいねん。"
        reply = "オカン、頑張って！ 思い出して!"
    else:
        if is_anti:
            speech = random.choice([
                f"それがわからないねん。オカンが言うには、[{feat}]らしいねん。",
                f"まだ、わからんねん。オカン、[{feat}]って言ってたねん。"
            ])
            if len(feat) > 30:
                root = False
                doc = nlp(feat)
                feat = ''
                candidate_present = []
                for token in doc:
                    if token.dep_ in ['advcl', 'ROOT']:
                        root = True
                    if token.orth_ in ['、', '。']:
                        if root:
                            candidate_present.append(feat)
                        root = False
                        feat = ''
                    else:
                        feat += token.orth_
                feat = random.choice(candidate_present)
            if len(feat) > 30:
                reply = f"ほな[{theme}]とちがうか。"
            else:
                reply = f"{theme}と違うか！{theme}で[{feat}]はあり得ないことなんよ。ほな[{theme}]ちゃうがなそれ。"
        else:
            speech = random.choice([
                f"オカンが言うには、[{feat}]って言うねんな。",
                f"オカン曰く、[{feat}]らしいねん。"
            ])
            reply = random.choice([
                f"[{theme}]やないかい! その特徴はもう完全に[{theme}]やがな。すぐわかったよこんなもん。",
                f"[{theme}]やないかい! それは完全に[{theme}]や。簡単よ。"
            ])
    return speech, reply


def shape_soup(soup, is_anti=True):
    """
        soupを整形して必要なpタグのみ残す。is_anti=Falseでpタグが少ない場合、liタグも追加
    """
    soup = soup.find('div', {"class": 'mw-content-container'})
    # 余分なタグを個別に除外
    extras = ['table', 'small', 'sup']
    for extra in extras:
        for ex in soup.find_all(extra):
            ex.decompose()
    try:
        soup.find('div', {"class": 'thumb'}).decompose()
    except AttributeError:
        pass
    try:
        soup.find('li', {"class": 'gallerybox'}).decompose()
    except AttributeError:
        pass
    texts = soup.find_all('p')[:P_TAGS_MAX]
    # feat_X用にpタグが少ない場合はliタグも追加
    if len(texts) < 5 and not is_anti:
        try:
            soup.find('div', {"role": 'navigation'}).decompose()
        except AttributeError:
            pass
        for ol in soup.find_all('ol', class_='references'):
            ol.decompose()
        try:
            soup.find('div', {'id': 'catlinks'}).decompose()
        except AttributeError:
            pass
        soup.find('nav').decompose()
        texts += soup.find_all('li')[:P_TAGS_MAX]
    return texts


def get_soup(url):
    """
        特徴文作成のためにwikiの本文を抽出する
    """
    text = requests.get(url).text
    soup = BeautifulSoup(text, features="html.parser")
    if soup is None:
        raise ResultNoneException(f"{url}のsoup")
    return soup


def get_category_soup(category):
    """
        カテゴリー記事のsoupを取得する
    """
    url = f"{BASE_WIKI}/Category:{category}"
    return get_soup(url)


def get_theme_soup(theme):
    """
        記事のsoupを取得する
    """
    url = f"{BASE_WIKI}/{theme}"
    return get_soup(url)


def get_category_info(url):
    """
        カテゴリーに属する記事数と、条件を満たすカテゴリーのリストを返す。handlerに与えて非同期処理する
    """
    try:
        soup = get_soup(url)
    except ResultNoneException:
        # 存在しないページの場合
        print(f"{url}のページは存在しません")
        return 0, []

    soup = soup.find('div', id='mw-pages')
    if soup is None:
        # 所属するページが存在しない（サブカテゴリーしかない場合）
        print(f"{url}に所属するページはありません")
        return 0, []

    category_element_num_sentence = soup.find('p').getText(strip=True)
    if category_element_num_sentence == "このカテゴリには以下のページのみが含まれています。":
        category_element_num = 1
    else:
        category_element_num = int(re.sub(r"\D", "", category_element_num_sentence[:20]))

    category_elements = []
    groups = soup.find_all(class_="mw-category-group")
    for group in groups:
        if re.fullmatch(r"[ぁ-ゟa-zA-Z1-9|*]+", group.find('h3').getText()):
            elements = group.find_all('a')
            for ele in elements:
                category_elements.append(ele.getText())

    return category_element_num, category_elements


def get_present(article=''):
    """
        wikipediaの記事からプレゼントを取得する
    """
    pattern = [
        {"POS": {"IN": ["NUM", "NOUN", "PROPN", "ADV"]}, "OP": "+"},
        {"TEXT": {"IN": ["の", "な"]}},
        {"POS": {"IN": ["NUM", "NOUN", "PROPN"]}, "OP": "*"},
        {"TEXT": "の", "OP": "?"},
        {"POS": {"IN": ["NUM", "NOUN", "PROPN"]}, "OP": "*"},
        {"TEXT": "の", "OP": "?"},
        {"POS": {"IN": ["NUM", "NOUN", "PROPN"]}, "OP": "+"}
    ]
    matcher.add("present", [pattern])
    # t = time.time()
    present = ''
    url = f'{BASE_WIKI}/{article}' if article != '' else RANDOM_WIKI
    print(f"プレゼント取得用url：{url}")
    soup = get_soup(url)
    p_tags = shape_soup(soup, is_anti=True)
    max_len = 0
    for p_tag in p_tags:
        text = p_tag.getText()
        # t2 = time.time()
        try:
            doc = nlp(text)
        except IndexError:
            continue
        for _, first_ind, last_ind in matcher(doc):
            candidate_present = doc[first_ind:last_ind].text
            if len(candidate_present) > max_len:
                present = candidate_present
                max_len = len(candidate_present)
    print(f"プレゼントの候補：{present}")
    # new_t = time.time()
    # print(len(p_tags), time.time()-t)
    # t = new_t
    return present


def make_replace_words(word_key, texts, true_word=None):
    """
        特徴文中で置換する必要のあるワードを収集する。置換しないとネタバレになってしまうテーマに近い単語が該当
    """
    # 括弧除去
    word = re.sub(r"\(.+?\)", "", word_key)
    # スペース除去
    word2 = re.sub(r" ", "", word)
    replace_words = [word, word2]

    # word2に含まれる固有名詞を収集(antiの場合はtrue_wordを追加)
    replace_sub_words = []
    for sent in nlp(word2).sents:
        tokens = [token.orth_ for token in sent if '人名' in token.tag_]
        tokens2 = [token.orth_ + '氏' for token in sent if '人名' in token.tag_]
        if len(tokens) > 0:
            replace_sub_words += tokens
            replace_sub_words += tokens2
    if '・' in word:
        replace_sub_words += word2.split('・')
    if true_word is not None:
        replace_words.append(true_word)
    # print(replace_words)

    # 別名を収集
    # print(word_key, texts)
    summary = texts[0].getText() if len(texts) else ""
    rubies = re.search(r"(?<=（).+?(?=）)", summary)
    if rubies is not None and rubies.start() < len(word) * 2:
        replace_words.append(summary[:rubies.start()])
        for rubi in rubies.group().replace("　", "").split("、"):
            w = re.sub(r" ", "", re.sub(r".+：", "", re.sub(r".+:", "", rubi)))
            if len(w) > 0:
                replace_words.append(w)
    # print(replace_words, replace_sub_words)
    return replace_words, replace_sub_words


def replace_theme(sent, cat, words, sub_words):
    """
        sent（特徴文）中でテーマのネタバレになってしまう単語を「その『カテゴリー名』」に置換する
    """
    sent = sent.replace(r"\n", "")
    for replace_word in words:
        sent = sent.replace(replace_word, f"「その{cat}」")
    ad_positions = ['の', 'に', 'は', 'と', 'も', 'が', 'を', 'へ']
    for sub_word in sub_words:
        for ad_position in ad_positions:
            sent = sent.replace(sub_word + ad_position, f"「その{cat}」{ad_position}")
    return sent


def shape_text(sent, cat, words, sub_words, first=False):
    """
        特徴文を整形する
    """
    sent = sent.replace(" ", "").replace("　", "")
    if len(sent) == 0:
        raise EmptySentenceException
    if sent[-1] in '、」':
        raise InvalidSentenceException(f"文末が{sent[-1]}で終わっている", sent)

    # 一文目の禁止ワード
    pre = ['これ', 'それ', 'この', 'その', 'あの', 'ここ', 'そこ', 'こう', 'そう', '以上', '上記', '上述']
    # 全てに共通する禁止ワード
    post = ['以下', '下記', '下表', '※', '次の', '凡例', '参照', '別途', '記載', '記述', '述べる', 'ISBN', '出典', '本項', '\\']
    for word in post:
        if word in sent:
            raise InvalidSentenceException("禁止ワードを含む", sent)

    if sent[:3] in ["また、", "なお、"]:
        sent = sent[3:]
    elif sent[:2] in ["また", "なお"]:
        sent = sent[2:]

    tokens = nlp(sent)
    if tokens[-1].pos_ == 'SPACE':
        if len(tokens) == 1:
            raise EmptySentenceException
        tokens = tokens[:-1]

    if tokens[-1].pos_ in ['PUNCT', 'ADP', 'CCONJ']:
        tokens = tokens[:-1]

    if first:
        if tokens[0].pos_ in ['ADP', 'CCONJ']:
            raise InvalidSentenceException("一文目の文頭が助詞または接続詞である", sent)

        for i, token in enumerate(tokens):
            for pr in pre:
                if pr in token.orth_ and i < 10:
                    raise InvalidSentenceException(f"一文目の{i + 1}語目に指示語を含む", sent)
            if token.pos_ == 'PUNCT':
                break
    sent = replace_theme(str(tokens), cat, words, sub_words)
    replace_flg = 'その' + cat in sent
    return sent, replace_flg
