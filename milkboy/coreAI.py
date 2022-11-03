import sys
import time

import numpy as np
import wikipedia

try:
    from .exception import NoResultException, ResultNoneException, \
        FailError, InvalidSentenceException, EmptySentenceException
except ImportError:
    from exception import NoResultException, ResultNoneException, \
        FailError, InvalidSentenceException, EmptySentenceException
try:
    from .utils import *
except ImportError:
    from utils import *

wikipedia.set_lang("ja")

# global
FEAT_MIN = 15
FEAT_MAX = 70
# SUMMARY_MIN = 20
# SUMMARY_MAX = 70
CAT_ELE_MIN = 10
CAT_ELE_MAX = 1000
CAT_NUM_MAX = 6
BASE_WIKI = 'https://ja.wikipedia.org/wiki'
RANDOM_WIKI = f'{BASE_WIKI}/Special:Random'


def select_neta_words(theme: str, category: str, category_articles: list[str], num: int) -> tuple[list[str], list[str], str]:
    """
        カテゴリーに属するテーマ記事の中からpresentを1個と、predictionsを2個と、anti_themeをランダムにnum個選ぶ
    """
    # 記事リストを作る
    category_article_list = []
    category_article_sub_list = []
    theme = re.sub(r" ", "", re.sub(r"\(.+?\)", "", theme))
    category = re.sub(r" ", "", re.sub(r"\(.+?\)", "", category))

    for ele in category_articles:
        ele = re.sub(r" ", "", re.sub(r"\(.+?\)", "", ele))
        if 'Template:' in ele:
            continue
        elif ele in theme or theme in ele or \
                ele in category or category in ele:
            category_article_sub_list.append(ele)
        else:
            category_article_list.append(ele)
            # print(f"アンチテーマの候補：{ele}")

    if len(category_article_list) == 0:
        if len(category_article_sub_list) == 0:
            raise NoResultException(f"「{category}」の適切なカテゴリー要素")
        category_article_list = category_article_sub_list

    # 記事リストからpresentを選ぶ
    article_for_present = random.choice(category_article_list)
    present = get_present(article_for_present)

    # 記事リストからpredictionsを選ぶ
    if len(category_article_list) == 1:
        predictions = [category_article_list[0], '']
    else:
        predictions = random.sample(category_article_list, 2)

    # 記事リストからアンチテーマをnum個選ぶ
    anti_themes = random.sample(category_article_list, min(len(category_article_list), num))

    return anti_themes, predictions, present


def get_sub_category(category: str, sub=True) -> str:
    """
        カテゴリーページにアクセスし、適切なサブカテゴリーを1つ選んで返す
    """
    soup = get_category_soup(category)

    subcategories_soup = soup.find(id='mw-subcategories')
    if subcategories_soup is None:
        raise ResultNoneException(f"{category}ページをid='mw-subcategories'で検索したsoup")

    sub_categories = []
    for group in subcategories_soup.find_all('ul'):
        information = group.find_all(class_='CategoryTreeItem')
        for info in information:
            title = info.find_all('span')[-1]['title']
            nums = list(map(int, re.findall(r'\d+', title)))
            if (sub and nums[0] >= 1) or (not sub and CAT_ELE_MIN <= nums[1] <= CAT_ELE_MAX):
                sub_categories.append(info.find('a').getText())

    if len(sub_categories) == 0:
        raise NoResultException(f"{category}のsub_categories")

    sub_category = random.choice(sub_categories)

    return sub_category


def get_category_elements(category: str) -> list[str]:
    """
        カテゴリーページにアクセスし、カテゴリーに属するテーマのリストを取得する
    """
    soup = get_category_soup(category)

    mw_pages_soup = soup.find('div', id='mw-pages')
    if mw_pages_soup is None:
        raise ResultNoneException(f"{category}ページをid='mw-pages'で検索したsoup")

    category_elements = []
    groups = mw_pages_soup.find_all(class_="mw-category-group")
    category = re.sub(r" ", "", re.sub(r"\(.+?\)", "", category))
    for group in groups:
        if re.fullmatch(r"[ぁ-ゟa-zA-Z]+", group.find('h3').getText()):
            a_tags = group.find_all('a')
            for a_tag in a_tags:
                ele = re.sub(r" ", "", re.sub(r"\(.+?\)", "", a_tag.getText()))
                if ele not in category and category not in ele \
                        and 'Template:' not in ele:
                    category_elements.append(ele)

    return category_elements


def gather_feats(category, word_key, soup, is_anti, true_word=None):
    """
        候補となるアンチ特徴文をかき集める
    """
    texts = shape_soup(soup, is_anti)
    replace_words, replace_sub_words = make_replace_words(word_key, texts, true_word)
    first_feat = ''
    # 一文目を処理するまでTrue
    first = True
    feats = []
    feat_supplement = []
    # メタ文字+?で最短一致 （x（x）x）、(x(x)x)、（x）、(x)、[x]
    extras = [r"（[^）]+（.+?）[^（]+）", r"\([^）]+\(.+?\)[^（]+\)", "（.+?）", r"\(.+?\)", r"\[+.+\]+"]
    for p_tag in texts:
        feat = ''
        replace = False
        text = p_tag.getText()
        if first:
            text = re.sub(r"^.+?）は、", "", text)
            text = re.sub(r"^.+?）とは、", "", text)
            text = re.sub(r"^.+?）は", "", text)
            text = re.sub(r"^.+?）とは", "", text)
            first = False
        for extra in extras:
            text = re.sub(extra, "", text)
        if len(text) < 5:
            continue
        doc = text.replace('\n', '').split('。')
        for i, sent in enumerate(doc):
            try:
                first_sent = (i == 0)
                sent, replace_flg = shape_text(sent, category, replace_words, replace_sub_words, first_sent)
            except InvalidSentenceException as e:
                print(e)
                break
            except EmptySentenceException:
                continue
            if first_feat == '' and feat == '':
                feat += sent + '。'
            elif len(feat) + len(sent) + 1 <= FEAT_MAX:
                feat += sent + '。'
            else:
                break
            replace |= replace_flg
        if len(feat) >= FEAT_MIN:
            # print(feat, first_feat)
            if first_feat == '':
                first_feat = feat
            elif replace or is_anti:
                feats.append(feat)
            else:
                feat_supplement.append(feat)
    return feats if is_anti else (first_feat, feats, feat_supplement)


def select_category_from_theme(theme, soup=None):
    """
        テーマが属するカテゴリーの中から条件を満たすものを選び出す
    """
    if soup is None:
        soup = get_theme_soup(theme)

    word = re.sub(r" ", "", re.sub(r"\(.+?\)", "", theme))
    category_num_cnt = 0
    urls = []
    categories = []
    prohibit_category = ['議論が行われているページ', '告知事項があるページ', '同名の作品', '誤表記',
                         '提案があるページ', '質問があるページ', '確認・注意事項があるページ']

    category_links = soup.find('div', id='mw-normal-catlinks').find('ul').find_all('li')

    for category_link in category_links:
        # print('start', time.time()-t)
        category_name = category_link.getText()

        # 不適切なカテゴリーの除外
        if "曖昧さ回避" in category_name:
            continue
        if category_name in prohibit_category \
                or theme in category_name \
                or category_name in theme \
                or word in category_name \
                or category_name in word:
            continue
        # 2桁以上の数字が含まれているカテゴリー名は除外する
        if re.search(r'.\d\d', category_name) is not None:
            continue

        categories.append(category_name)

        category_page_title = category_link.find('a')['title']
        url = f"{BASE_WIKI}/{category_page_title}"
        urls.append(url)

        category_num_cnt += 1
        if category_num_cnt == CAT_NUM_MAX:
            break

    loop = asyncio.new_event_loop()
    data = loop.run_until_complete(handler(loop, urls, get_category_info))

    # カテゴリーに属する記事数によりカテゴリーを選別
    normal_categories, large_categories = [], []
    for category, (category_element_num, category_elements) in zip(categories, data):
        if CAT_ELE_MIN <= category_element_num <= CAT_ELE_MAX:
            normal_categories.append((category, category_elements))
        else:
            large_categories.append((category_element_num, category, category_elements))

    if len(normal_categories) == 0:
        if len(large_categories) == 0:
            raise NoResultException("入力されたテーマに対応するカテゴリー")
        large_categories.sort()
        # if ind >= len(large_categories): ind = 0
        ind = np.random.binomial(len(large_categories) - 1, 0.4)
        category = large_categories[ind][1:]
        return category

    ind = np.random.binomial(len(normal_categories) - 1, 0.4)
    # if ind >= len(normal_categories): ind = 0
    category = normal_categories[ind]
    return category


def select_category_from_genre(genre):
    """
        与えられたジャンルに属するカテゴリーとカテゴリー要素を選ぶ
    """
    # 下位カテゴリ移動1回目
    category = get_sub_category(genre, sub=True)
    if random.randint(0, 1):
        try:
            # 下位カテゴリ移動2回目
            category = get_sub_category(category, sub=True)
        except (ResultNoneException, NoResultException) as e:
            print(e)
    try:
        # 下位カテゴリ移動3回目
        category = get_sub_category(category, sub=True)
    except (ResultNoneException, NoResultException) as e:
        print(e)
    while True:
        try:
            # カテゴリに属する記事を取得
            category_elements = get_category_elements(category)
        except ResultNoneException as e:
            print(e)
            # 属するページがなく下位カテゴリしか存在しないカテゴリーの場合、下位カテゴリーを取得
            category = get_sub_category(category)
        else:
            break
    return category, category_elements


def select_true_feats(category, theme, true_soup, num):
    """
        カテゴリーとテーマと記事のsoupからfeat_Xをnum個生成
    """
    first_feat, feats, feat_supplement = gather_feats(category, word_key=theme, soup=true_soup, is_anti=False)
    if first_feat != '':  # featXで、featが一つは見つかった場合
        if len(feats) >= num - 1:
            feats = [first_feat] + random.sample(feats, num-1)
        else:
            feats = [first_feat] + feats \
                    + random.sample(feat_supplement, min(len(feat_supplement), num - 1 - len(feats)))
    elif len(feats) + len(feat_supplement) == 0:
        feats = ['']
    elif len(feats) >= num:
        feats = random.sample(feats, num)
    else:
        feats += random.sample(feat_supplement, min(len(feat_supplement), num - len(feats)))
    return feats


def select_anti_feat(category, anti_theme, anti_soup, prob, true_word):
    """
        カテゴリーとアンチテーマと記事のsoupからanti_feat_Xを1個選択
    """
    feats = gather_feats(category, word_key=anti_theme, soup=anti_soup, is_anti=True, true_word=true_word)
    if len(feats) >= 1:
        # 二項分布でanti_featsの中からfeatsを一つ洗濯する
        ind = np.random.binomial(len(feats) - 1, prob)
        feat = feats[ind]
    else:
        feat = ''
    return feat


def make_all_feats(category, theme, anti_themes):
    """
        カテゴリ、テーマと全てのアンチテーマに対して特徴文を出力
    """
    urls = [f"https://ja.wikipedia.org/wiki/{word}" for word in [theme] + anti_themes]
    loop = asyncio.new_event_loop()
    soups = loop.run_until_complete(handler(loop, urls, get_soup))

    anti_feats = []
    anti_soups = soups[1:]
    for anti_theme, anti_soup in zip(anti_themes, anti_soups):
        anti_feat = select_anti_feat(category, anti_theme, anti_soup, prob=0.5, true_word=theme)
        anti_feats.append(anti_feat)
    if len(anti_feats) == 0:
        anti_feats = [""]

    feats = select_true_feats(category, theme, true_soup=soups[0], num=len(anti_feats))
    if len(feats) == 0:
        feats = [""]
        anti_feats = [""]

    return feats, anti_feats


def generate_stages(input_theme, theme, anti_themes, category, seed_num, stage_max, predictions, present):
    """
        全ステージを生成
    """
    # 特徴文生成
    feats, anti_feats = make_all_feats(category, theme, anti_themes[:-1])
    # print(feats)
    # print(anti_feats)
    stage_num = min(min(len(feats), len(anti_feats)) + 1, stage_max)
    stage_dicts = []
    # normal stage
    stage = i = 0
    for _ in range(stage_num - 1):
        stage_dict = dict(input_theme=input_theme, theme=theme, seed=seed_num, category=category)
        stage_dict["stage"] = stage
        stage_dict["featX"], stage_dict["featX_reply"] = feat_to_script(feat=feats[stage], is_anti=False, theme=theme)

        while i < len(anti_feats) and anti_feats[i] == '':
            i += 1
        if i >= len(anti_feats):
            break
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
        dict(
            input_theme=input_theme,
            theme=theme,
            stage=-1,
            seed=seed_num,
            next_is_last=True,
            category=category,
            anti_theme=anti_themes[-1],
            featX="わからへん",
            featX_reply=f"わからへんことない！おかんの好きな [{category}] は[{theme}]!",
            anti_featX=f"オカンがいうには[{theme}]ではないっていうてた。",
            anti_featX_reply=f"先言えよ！",
            conjunction=f"申し訳ないなと思って。オトンがいうには、[{anti_themes[-1]}] ちゃうかって。"
        )
    )
    stage_dicts[0]['present'] = present
    stage_dicts[0]['prediction1'], stage_dicts[0]['prediction2'] = predictions[0], predictions[1]
    print('last of generate_stages')
    return stage_dicts


def generate_story_list(input_theme, seed_num, stage_max, genre=None):
    """
        全体処理
    """
    np.random.seed(seed_num)
    # ジャンルモード
    if genre is not None:
        print(genre)
        while True:
            category, category_articles = select_category_from_genre(genre)
            if len(category_articles) == 0:
                continue
            theme = random.choice(category_articles)
            print(f"ジャンルモード「カテゴリー：{category}、テーマ：{theme}」")
            try:
                anti_themes, predictions, present = select_neta_words(theme, category, category_articles, stage_max)
            except NoResultException as e:
                print(e)
                continue
            break
        if stage_max == 0:
            return get_present_only(present, seed_num)
        random.seed(seed_num)
        return generate_stages(input_theme, theme, anti_themes, category, seed_num, stage_max, predictions, present)
    # テーマモード
    if input_theme in ['', 'random']:
        # テーマランダムモード
        while True:
            try:
                soup = get_soup(RANDOM_WIKI)
                theme = soup.find('head').find('title').getText().replace(' - Wikipedia', '')
                category, category_articles = select_category_from_theme(theme, soup)
                print(f"テーマ：{theme}、カテゴリー：{category}、カテゴリー要素数：{len(category_articles)}")
                break
            except (AttributeError, NoResultException) as e:
                print(e)
                continue
    else:
        # テーマノーマルモード
        searched_list = wikipedia.search(input_theme)
        # print(searched_list)
        # print("search:",time.time()-t)
        for theme in searched_list:
            print(f"テーマ候補：{theme}")
            try:
                category, category_articles = select_category_from_theme(theme)
            except (AttributeError, NoResultException) as e:
                print(e)
            else:
                print(f"カテゴリー：{category}、記事数：{len(category_articles)}")
                # print("select_category_from_theme:", time.time()-t)
                break
        else:
            raise FailError("カテゴリー選択")
    anti_themes, predictions, present = select_neta_words(theme, category, category_articles, stage_max)
    if stage_max == 0:
        return get_present_only(present, seed_num)
    # print("select_neta_words:", time.time()-t)
    if len(anti_themes) > 0:
        print('last of generate_story_list')
        return generate_stages(input_theme, theme, anti_themes, category, seed_num, stage_max, predictions, present)
    return generate_story_list(input_theme, seed_num, stage_max)


if __name__ == "__main__":
    args = sys.argv
    test_theme = args[1] if len(args) >= 2 else 'random'
    trial_times = int(args[2]) if len(args) >= 3 else 1

    start = time.time()
    t = start
    power = 0
    for cnt in range(trial_times):
        print(f"{cnt + 1}回目")
        test_seed = int(args[2]) if len(args) > 2 else random.randint(0, 100000)
        generated_story = generate_story_list(input_theme=test_theme, seed_num=test_seed, stage_max=4)
        # pprint(generated_story)
        new_t = time.time()
        power += (new_t - t) ** 2
        t = new_t
        print()
    total = t - start
    print("実行時間の平均値：", total / trial_times)
    # 1回のみ実行の場合は0になる
    print("実行時間の標準偏差：", (power / trial_times - (total / trial_times) ** 2) ** 0.5)
