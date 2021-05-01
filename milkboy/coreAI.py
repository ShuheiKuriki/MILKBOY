import wikipedia
import re
import asyncio
import requests
import sys
import numpy as np
import random
from pprint import pprint
from bs4 import BeautifulSoup
import spacy
from spacy.matcher import Matcher

nlp = spacy.load('ja_ginza')
wikipedia.set_lang("ja")
matcher = Matcher(nlp.vocab)

# global
FEAT_MIN = 15
FEAT_MAX = 70
# SUMMARY_MIN = 20
# SUMMARY_MAX = 70
CAT_MEM_MIN = 10
CAT_MEM_MAX = 1000
CAT_NUM_MAX = 6
PTAGS_MAX = 15
RANDOM_WIKI = 'https://ja.wikipedia.org/wiki/Special:Random'


def get_tsukami():
    pattern = [
        {"POS": {"IN": ["NUM", "NOUN", "PROPN", "ADV"]}, "OP": "+"},
        {"TEXT": {"IN": ["の", "な"]}},
        {"POS": {"IN": ["NUM", "NOUN", "PROPN"]}, "OP": "*"},
        {"TEXT": "の", "OP": "?"},
        {"POS": {"IN": ["NUM", "NOUN", "PROPN"]}, "OP": "*"},
        {"TEXT": "の", "OP": "?"},
        {"POS": {"IN": ["NUM", "NOUN", "PROPN"]}, "OP": "+"}
    ]
    matcher.add("tsukami", None, pattern)
    # t = time.time()
    tsukami = ''
    while len(tsukami) < 10:
        ptags = BeautifulSoup(requests.get(RANDOM_WIKI).text, "html.parser").find_all('p')
        max_len = 0
        for ptag in ptags:
            text = ptag.getText()
            # t2 = time.time()
            doc = nlp(text)
            for _, start, end in matcher(doc):
                cand = doc[start:end].text
                if len(cand) > max_len:
                    tsukami = cand
                    max_len = len(cand)
    # new_t = time.time()
    # print(len(ptags), time.time()-t)
    # t = new_t
    return tsukami


def get_catinfo(url):
    """
    カテゴリーに属する記事数を数える。handlerに与えて非同期処理する
    """
    # t1 = time.time()
    # print('start:',t1-t)
    text = requests.get(url).text
    # t2 = time.time()
    # print("mid", t2-t1, len(text))
    soup = BeautifulSoup(text, "html.parser").find('div', id='mw-pages')
    catmems = []
    try:
        sent = soup.find('p').getText(strip=True)[:20]
        groups = soup.find_all(class_="mw-category-group")
        for group in groups:
            if re.fullmatch('[ぁ-ゟa-zA-Z]+', group.find('h3').getText()):
                mems = group.find_all('a')
                for mem in mems:
                    catmems.append(mem.getText())
    except:
        return '0', []
    # t3 = time.time()
    # print("end", t3-t2, len(res))
    return sent, catmems


def get_soup(url):
    """
    特徴文作成のためにwikiの本文を抽出する。handlerに与えて非同期処理する
    """
    text = requests.get(url).text
    soup = BeautifulSoup(text, features="html.parser")
    return soup


async def handler(loop, urls, func):
    """
    非同期処理
    """
    async def async_ex(url):
        async with asyncio.Semaphore(20):
            return await loop.run_in_executor(None, func, url)
    tasks = [async_ex(url) for url in urls]
    return await asyncio.gather(*tasks)


def choose_cat(word_key, soup=None):
    """
    テーマのカテゴリー選択
    """
    if soup is None:
        url = f'https://ja.wikipedia.org/wiki/{word_key}'
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
    li_tags = soup.find('div', id='mw-normal-catlinks').find('ul').find_all('li')
    word = re.sub(" ", "", re.sub("\(.+?\)", '', word_key))
    # print(word)
    cnt = 0
    urls = []
    cats = []
    prohibit = ['議論が行われているページ', '告知事項があるページ', '同名の作品',
                '提案があるページ', '質問があるページ', '確認・注意事項があるページ']
    for li in li_tags:
        # print('start',time.time()-t)
        li_text = li.getText()

        # 不適切なカテゴリーの除外
        if "曖昧さ回避" in li_text or li_text in prohibit \
                or word_key in li_text or word in li_text \
                or li_text in word_key or li_text in word:
            continue
        if re.search('.[0-9][0-9]', li_text) is not None:
            continue

        cat_key = li.find('a')['title']
        cats.append(li_text)
        url = f'https://ja.wikipedia.org/wiki/{cat_key}'
        urls.append(url)
        cnt += 1
        if cnt == CAT_NUM_MAX: break

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(handler(loop, urls, get_catinfo))

    # カテゴリーに属する記事数によりカテゴリーを選別
    small_cats, big_cats = [], []
    for cat, (sent, catmems) in zip(cats, data):
        cat_mem_n = int(re.sub(r"\D", "", sent))
        if CAT_MEM_MIN <= cat_mem_n <= CAT_MEM_MAX:
            small_cats.append((cat, catmems))
        else:
            big_cats.append((cat_mem_n, cat, catmems))
    big_cats.sort()

    if len(small_cats) > 0:
        ind = np.random.binomial(len(small_cats)-1, 0.5)
        # if ind >= len(small_cats): ind = 0
        return small_cats[ind]
    if len(big_cats) == 0: return False
    # if ind >= len(big_cats): ind = 0
    ind = np.random.binomial(len(big_cats)-1, 0.5)
    return big_cats[ind][1:]


def make_replace_words(word_key, texts, true_word):
    """
    特徴文中において置換する必要のあるテーマの代替ワードを収集
    """
    # 括弧除去
    word = re.sub("\(.+?\)", '', word_key)
    # スペース除去
    word2 = re.sub(" ", '', word)
    replace_words = [word, word2]

    # word2に含まれる固有名詞を収集(antiの場合はtrue_wordを追加)
    replace_subwords = []
    for sent in nlp(word2).sents:
        tokens = [token.orth_ for token in sent if '人名' in token.tag_]
        tokens2 = [token.orth_+'氏' for token in sent if '人名' in token.tag_]
        if len(tokens) > 0:
            replace_subwords += tokens
            replace_subwords += tokens2
    if '・' in word:
        replace_subwords += word2.split('・')
    if true_word is not None:
        replace_words.append(true_word)
    # print(replace_words)

    # 別名を収集
    # print(word_key, texts)
    summary = texts[0].getText() if len(texts) else ""
    rubis = re.search(r'(?<=\（).+?(?=\）)', summary)
    if rubis is not None and rubis.start() < len(word)*2:
        replace_words.append(summary[:rubis.start()])
        for rubi in rubis.group().replace('　', '').split('、'):
            w = re.sub(' ', '', re.sub(".+：", '', re.sub(".+:", '', rubi)))
            if len(w) > 0:
                replace_words.append(w)
    # print(replace_words, replace_subwords)
    return replace_words, replace_subwords


def replace_theme(sent, cat, words, subwords):
    for replace_word in words:
        sent = sent.replace(replace_word, f'「その{cat}」')
    adps = ['の', 'に', 'は', 'と', 'も', 'が', 'を', 'へ']
    for subword in subwords:
        for adp in adps:
            sent = sent.replace(subword+adp, f'「その{cat}」{adp}')
    return sent.replace('\n', '')


def shape_text(sent, cat, words, subwords, first=False):
    sent = sent.replace(' ', '').replace('　', '')
    if len(sent) == 0 or sent[-1] == '、':
        return '', False
    pre = ['これ', 'それ', 'この', 'その', 'あの', 'ここ', 'そこ', 'こう', 'そう', '以上', '上記']
    post = ['以下', '下記', '下表', '※', '次の', '凡例', '参照', '別途', '記載', '述べる', 'ISBN', '出典']
    for word in post:
        if word in sent:
            return False, False
    tokens = nlp(sent)
    if first and tokens[0].pos_ == 'ADP':
        return False, False
    if tokens[-1].pos_ == 'PUNCT':
        return False, False
    if first and tokens[0].pos_ == 'CCONJ':
        tokens = tokens[2:] if tokens[1].pos_ == 'PUNCT' else tokens[1:]
    if first:
        for token in tokens:
            if token.orth_ in pre: return False, False
            if token.pos_ == 'PUNCT': break
            if token.dep_ == 'nsubj' and token.pos_ == 'PROPN' and token.orth_ not in words+subwords:
                if token.head.i >= len(tokens)-7:
                    return False, False
    sent = replace_theme(str(tokens), cat, words, subwords)
    if 'その'+cat in sent:
        return sent, True
    return sent, False


def shape_soup(soup, true_word):
    # 余分なpタグを個別に除外
    extras = ['table', 'small', 'sup']
    for extra in extras:
        for ex in soup.find_all(extra):
            ex.decompose()
    try:
        soup.find('span', {"id": 'coordinates'}).decompose()
    except:
        pass
    try:
        soup.find('div', {"class": 'thumb'}).decompose()
    except:
        pass
    try:
        soup.find('li', {"class": 'gallery'}).decompose()
    except:
        pass
    texts = soup.find_all('p')[:PTAGS_MAX]
    # feat_X用にpタグが少ない場合はliタグも追加
    if len(texts) < 5 and true_word is None:
        try:
            soup.find('div', {"role": 'navigation'}).decompose()
        except:
            pass
        try:
            for ol in soup.find_all('ol', class_='references'):
                ol.decompose()
        except:
            pass
        soup.find('div', {'id': 'catlinks'}).decompose()
        soup.find('div', {'id': 'mw-panel'}).decompose()
        soup.find('footer').decompose()
        soup.find('nav').decompose()
        texts += soup.find_all('li')[:PTAGS_MAX]
    return texts


def make_feats(cat, word_key, soup, num, true_word=None):
    """
    ワードとカテゴリーと記事の情報から特徴文をnum個生成
    """
    texts = shape_soup(soup, true_word)
    # print(texts)
    replace_words, replace_subwords = make_replace_words(word_key, texts, true_word)
    first_feat = ''
    feat = ''
    flag = False
    # 一文目を処理するまでTrue
    first = True
    feat_set = []
    feat_suppli = []
    # メタ文字+?で最短一致
    extras = ["\（[^\）]+\（.+?\）[^\（]+\）", "\([^\）]+\(.+?\)[^\（]+\)", "\（.+?\）", "\(.+?\)", "\[+.+\]+"]
    for p_tag in texts:
        text = p_tag.getText()
        if first:
            text = re.sub("^.+?）は、", '', text)
            text = re.sub("^.+?）とは、", '', text)
            text = re.sub("^.+?）は", '', text)
            text = re.sub("^.+?）とは", '', text)
            first = False
        for extra in extras: text = re.sub(extra, '', text)
        if len(text) < 5: continue
        doc = text.split('。')
        for sent in doc:
            sent, flag2 = shape_text(sent, cat, replace_words, replace_subwords, first)
            if sent is False: break
            if len(sent) == 0: continue
            if first_feat == '' and feat == '':
                feat += sent+'。'
            elif len(feat)+len(sent)+1 <= FEAT_MAX: feat += sent+'。'
            else: break
            flag |= flag2
        if len(feat) >= FEAT_MIN:
            # print(feat, first_feat)
            if first_feat == '':
                first_feat = feat
            elif flag or true_word is not None:
                feat_set.append(feat)
            else:
                feat_suppli.append(feat)
        feat = ''
        flag = False
    if true_word:  # anti_featXの場合
        if len(feat_set) >= 1:
            ind = np.random.binomial(len(feat_set)-1, num)
            return feat_set[ind]
        return ''
    if first_feat != '':  # featXで、featが一つは見つかった場合
        if len(feat_set) >= num-1:
            indices = sorted(random.sample(range(len(feat_set)), num-1))
            return [first_feat] + list(np.array(feat_set)[indices])
        indices = sorted(random.sample(range(len(feat_suppli)), min(len(feat_suppli), num-1-len(feat_set))))
        return [first_feat] + feat_set + list(np.array(feat_suppli)[indices])
    if len(feat_set)+len(feat_suppli) == 0:
        return ['']
    if len(feat_set) >= num:
        indices = sorted(random.sample(range(len(feat_set)), num))
        return list(np.array(feat_set)[indices])
    indices = sorted(random.sample(range(len(feat_suppli)), min(len(feat_suppli), num-len(feat_set))))
    return feat_set + list(np.array(feat_suppli)[indices])


def make_all_feats(cat, theme, anti_themes):
    """
    カテゴリ、テーマと全てのアンチテーマに対して特徴文を出力
    """
    urls = [f'https://ja.wikipedia.org/wiki/{theme}']
    for anti in anti_themes:
        urls.append(f'https://ja.wikipedia.org/wiki/{anti}')
    loop = asyncio.get_event_loop()
    soups = loop.run_until_complete(handler(loop, urls, get_soup))
    anti_feats = []
    # num = len(anti_themes)
    for anti, soup in zip(anti_themes, soups[1:]):
        feat = make_feats(cat, anti, soup, 0.5, theme)
        anti_feats.append(feat)
    feats = make_feats(cat, theme, soups[0], max(1, len(anti_feats)))
    if len(feats) == 0:
        feats = [""]
        anti_feats = [""]
    elif len(anti_feats) == 0:
        anti_feats = [""]
    return feats, anti_feats


def feat_to_script(sent, is_anti, theme):

    if len(sent) == 0 and not is_anti:
        text = "オカンが言うには、これと言った特徴がないらしいねん。"
        text2 = "これと言った特徴がない?! お前のオカン、頑張って特徴を思い出してくれ。"
    elif len(sent) == 0 and is_anti:
        text = "オカン、それの特徴がもう思い出せないらしいねん。"
        text2 = "オカン、頑張って！ 思い出して!"
    else:
        res = sent
        if is_anti:
            text = random.choice([
                f"それがわからないねん。オカンが言うには、[{res}]らしいねん。",
                f"まだ、わからんねん。オカン、[{res}]って言ってたねん。"
                ])
            if len(sent) > 30:
                root = False
                doc = nlp(sent)
                sent = ''
                cand = []
                for token in doc:
                    if token.dep_ == 'ROOT':
                        root = True
                    if token.pos_ == 'PUNCT':
                        if root:
                            cand.append(sent)
                        root = False
                        sent = ''
                    else:
                        sent += token.orth_
                sent = random.choice(cand)
            if len(sent) > 30:
                text2 = f"ほな[{theme}]とちがうか。"
            else:
                text2 = f"{theme}と違うか！{theme}で[{sent}]はあり得ないことなんよ。ほな[{theme}]ちゃうがなそれ。"
        else:
            text = random.choice([
                f"オカンが言うには、[{res}]って言うねんな。",
                f"オカン曰く、[{res}]らしいねん。"
                ])
            text2 = random.choice([
                f"[{theme}]やないかい! その特徴はもう完全に[{theme}]やがな。すぐわかったよこんなもん。",
                f"[{theme}]やないかい! それは完全に[{theme}]や。簡単よ。"
                ])
    return text, text2


def generate_stages(input_theme, theme, anti_themes, cat, seed_num, stage_max, preds):
    """
    全ステージを生成
    """
    # 特徴文生成
    feats, anti_feats = make_all_feats(cat, theme, anti_themes[:-1])
    # print(feats)
    # print(anti_feats)
    stage_num = min(min(len(feats), len(anti_feats))+1, stage_max)
    stage_dicts = []
    # normal stage
    stage = i = 0
    for _ in range(stage_num-1):
        stage_dict = {"input_theme": input_theme, "theme": theme, "seed": seed_num, "category": cat}
        stage_dict["stage"] = stage
        stage_dict["featX"], stage_dict["featX_reply"] = feat_to_script(feats[stage], False, theme)

        while i < len(anti_feats) and anti_feats[i] == '':
            i += 1
        if i >= len(anti_feats): break
        stage_dict["anti_theme"] = anti_themes[i]
        stage_dict["anti_featX"], stage_dict["anti_featX_reply"] = feat_to_script(anti_feats[i], True, theme)
        i += 1

        stage_dict["next_is_last"] = False

        stage_dict["conjunction"] = random.choice([
            "もうちょっと詳しく教えてくれる？",
            "ほな、他に何か言ってなかった？"
            ])
        stage_dicts.append(stage_dict)
        stage += 1
    if len(stage_dicts):
        stage_dicts[-1]["next_is_last"] = True
    # last stage
    stage_dicts.append(
        {
            "input_theme": input_theme,
            "theme": theme,
            "stage": -1,
            "seed": seed_num,
            "next_is_last": True,
            "category": cat,
            "anti_theme": anti_themes[-1],
            "featX": "わからへん",
            "featX_reply": f"わからへんことない！おかんの好きな [{cat}] は[{theme}]!",
            "anti_featX": f"オカンがいうには[{theme}]ではないっていうてた。",
            "anti_featX_reply": f"先言えよ！",
            "conjunction": f"申し訳ないなと思って。オトンがいうには、[{anti_themes[-1]}] ちゃうかって。"
        }
    )
    stage_dicts[0]['tsukami'] = get_tsukami()
    stage_dicts[0]['pred1'], stage_dicts[0]['pred2'] = preds[0], preds[1]
    return stage_dicts


def choose_anti_themes(theme, cat, catmems, num):
    """
    anti_themeをランダムに選ぶ
    """
    catmem_list = []
    theme2 = re.sub(" ", "", re.sub("\(.+?\)", '', theme))
    cat2 = re.sub(" ", "", re.sub("\(.+?\)", '', cat))
    for mem in catmems:
        mem2 = re.sub(" ", "", re.sub("\(.+?\)", '', mem))
        if mem2 not in theme2 and theme2 not in mem2 and \
                mem2 not in cat2 and cat2 not in mem2:
            catmem_list.append(mem)
    if len(catmem_list) == 0:
        preds = ["", ""]
    elif len(catmem_list) == 1:
        preds = [catmem_list[0], '']
    else:
        preds = random.sample(catmem_list, 2)
    return random.sample(catmem_list, min(len(catmem_list), num)), preds


def tsukami_only():
    """つかみだけ"""
    return [
        {
            "input_theme": "",
            "theme": "",
            "stage": -1,
            "seed": 0,
            "next_is_last": True,
            "category": "",
            "anti_theme": "",
            "featX": "",
            "featX_reply": "",
            "anti_featX": "",
            "anti_featX_reply": "",
            "conjunction": "",
            "tsukami": get_tsukami()
        }
    ]


def generate_neta_list(input_theme, seed_num, stage_max):
    """
    全体処理
    """
    if stage_max == 0:
        return tsukami_only()
    random.seed(seed_num)
    np.random.seed(seed_num)
    if input_theme in ['', 'random']:
        while True:
            try:
                soup = BeautifulSoup(requests.get(RANDOM_WIKI).text, "html.parser")
                theme = soup.find('head').find('title').getText().replace(' - Wikipedia', '')
                cat, catmems = choose_cat(theme, soup)
                break
            except:
                pass
    else:
        searched_list = wikipedia.search(input_theme)
        # print(searched_list)
        # print("search:",time.time()-t)
        for theme in searched_list:
            try:
                cat, catmems = choose_cat(theme)
                # print("choose_cat:", time.time()-t)
                break
            except:
                pass
        else:
            return generate_neta_list(input_theme, seed_num, stage_max)
    anti_themes, preds = choose_anti_themes(theme, cat, catmems, stage_max)
    # print("choose_anti_themes:", time.time()-t)
    if len(anti_themes):
        return generate_stages(input_theme, theme, anti_themes, cat, seed_num, stage_max, preds)
    return generate_neta_list(input_theme, seed_num, stage_max)


if __name__ == "__main__":
    args = sys.argv
    input_theme = args[1] if len(args) > 1 else 'random'
    print(input_theme)
    import time
    start = time.time()
    t = start
    power = 0
    for i in range(1, 2):
        number = int(args[2]) if len(args) > 2 else random.randint(0, 100000)
        generated = generate_neta_list(input_theme=input_theme, seed_num=number, stage_max=4)
        pprint(generated)
        new_t = time.time()
        total = new_t-start
        power += (new_t - t) ** 2
        print(total / i)
        print((power/i - (total/i)**2)**0.5)
        t = new_t
