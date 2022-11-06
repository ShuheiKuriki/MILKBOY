"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import datetime
import random
import time

from twitter import Twitter, TwitterStream, OAuth

from milkboy.coreAI import generate_story_list
from milkboy.exception import FailError

try:
    from config.settings import prod
    AUTH = OAuth(prod.TW_TOKEN, prod.TW_TOKEN_SECRET, prod.TW_CONSUMER_KEY, prod.TW_CONSUMER_SECRET)
    print('import prod settings file')
except KeyError:
    from config.settings import dev
    AUTH = OAuth(dev.TW_TOKEN, dev.TW_TOKEN_SECRET, dev.TW_CONSUMER_KEY, dev.TW_CONSUMER_SECRET)
    print('import dev settings file')

API = Twitter(auth=AUTH)

MAX_TWEET_LEN = 130

GENRE_dic = {
    '日本の映画': 1,
    '日本の漫画': 1,
    'アニメ': 1,
    '日本のゲーム': 1,
    '日本の歴史': 1,
    '日本の地理': 1,
    '日本のスポーツ': 1,
    '日本の音楽': 1,
    '日本語の語句': 1,
    '日本の人物_(分野別)': 2,
    '日本の人物_(職業別)': 2,
    '物質': 1,
    '物理現象': 1,
    '数学的対象': 1,
    '計算機科学': 1,
    'random': 5
}

GENRES = []
for k, v in GENRE_dic.items():
    GENRES += [k]*v


def present_script(theme: str, present: str) -> tuple[str, str]:
    text1 = f"{datetime.datetime.now().strftime('%m月%d日 %H:%M:%S')}\n\n" \
           f"テーマ: {theme}\n\n" \
           f"内海「どうもーミルクボーイです。お願いします。」\n\n"
    text2 = "内海「あーありがとうございますー。"
    if len(present) >= 5:
        text2 += f'ね、今、[{present}]をいただきましたけどもね。こんなんなんぼあっても良いですからね、'
    else:
        text2 += 'ね、今、何もいただけませんでしたけどもね。何ももらえなくてもね、聞いてもらえるだけ'
    text2 += 'ありがたいですよ。いうとりますけどもね。」\n\n'
    return text1, text2


def introduction(category: str, prediction1: str, prediction2: str) -> list[str]:
    text1 = f'駒場「うちのおかんがね、好きな[{category}]があるらしいんやけど、その名前をちょっと忘れたらしくてね。」\n\n' \
           f'内海「好きな[{category}]忘れてもうて。どうなってんねんそれ。\n\n'

    text2 = f'内海「ほんでもおかんが好きな[{category}]なんて、[{prediction1}]か[{prediction2}]くらいでしょう。」\n\n' \
            f'駒場「それが違うらしいねんな」\n\n'

    text3 = f'内海「ほんだら俺がね、おかんの好きな[{category}]一緒に考えてあげるから、どんな特徴言うてたかとか教えてみてよ。」\n\n'
    return [text1, text2, text3]


def update_status(tweet_text: str, reply_id: int = None) -> dict:
    texts = []
    if len(tweet_text) > MAX_TWEET_LEN:
        left = 0
        right = MAX_TWEET_LEN
        texts.append(tweet_text[left:right])
        while right < len(tweet_text):
            left += MAX_TWEET_LEN
            right += MAX_TWEET_LEN
            texts.append(tweet_text[left:right])
    else:
        texts.append(tweet_text)
    if reply_id is None:
        tweet_info = API.statuses.update(status=texts[0])
    else:
        tweet_info = API.statuses.update(status=texts[0], in_reply_to_status_id=reply_id)
    for text in texts[1:]:
        tweet_info = API.statuses.update(status=text, in_reply_to_status_id=tweet_info['id'])
    return tweet_info


def multiple_tweets(texts: list[str], tweet_info: dict) -> dict:
    text = ''
    for tweet_text in texts:
        if len(text + tweet_text) <= MAX_TWEET_LEN:
            text += tweet_text
        elif len(text) == 0:
            tweet_info = update_status(tweet_text, tweet_info['id'])
        else:
            tweet_info = update_status(text, tweet_info['id'])
            text = tweet_text
    tweet_info = update_status(text, tweet_info['id'])
    return tweet_info


def tweet_story(story_list: list[dict]) -> dict:
    stage_num = len(story_list)
    first_stage = story_list[0] if len(story_list) > 1 else story_list[-1]
    prediction1, prediction2 = first_stage['prediction1'], first_stage['prediction2']
    if prediction1 == '' or prediction2 == '':
        raise FailError("予測ワード選択")
    theme = first_stage['theme']
    # つかみ
    first_tweet, second_tweet = present_script(theme, first_stage['present'])
    first_tweet_info = update_status(first_tweet)
    tweet_info = update_status(second_tweet, first_tweet_info['id'])
    # 導入
    intro = introduction(first_stage['category'], prediction1, prediction2)
    tweet_info = multiple_tweets(intro, tweet_info)
    for i in range(stage_num):
        story = story_list[i] if i < stage_num - 1 else story_list[-1]
        core_story = [
            f"駒場「{story['featX']}」\n\n",
            f"内海「{story['featX_reply']}」\n\n",
            f"駒場「{story['anti_featX']}」\n\n",
            f"内海「{story['anti_featX_reply']}」\n\n"
        ]
        if i != stage_num - 2:
            core_story.append(f"内海「{story['conjunction']}」\n\n")
        if i == stage_num - 1:
            core_story.append("内海「いや、絶対ちゃうやろ。」\n\n")
            core_story.append("内海「もうええわ、どうもありがとうございました。」\n\n")
        tweet_info = multiple_tweets(core_story, tweet_info)
    return first_tweet_info


def regular_tweet():
    res = 'start tweet'
    print(res)
    while res != 'tweet success':
        time.sleep(10)
        stage_max = 5
        genre_name = random.choice(GENRES)
        print(genre_name)
        for _ in range(10):
            seed = random.randint(0, 100000)
            try:
                if genre_name == 'random':
                    story_list = generate_story_list('random', seed, stage_max)
                else:
                    story_list = generate_story_list('', seed, stage_max, genre_name)
                tweet_story(story_list)
                break
            except FailError as e:
                print(e)
                continue
        res = 'tweet success'
    print(res)
    return


def auto_reply():
    twitter_stream = TwitterStream(auth=AUTH)
    print('activate auto reply')
    for call_tweet in twitter_stream.statuses.filter(language='ja', track='@milkboy_core_ai テーマ'):
        stage_max = 5
        try:
            print(f"リプライツイートアカウント名：{call_tweet['user']['name']}")
            print(f"ツイート内容：{call_tweet['text']}")
        except KeyError as e:
            print(e)
            continue
        theme = call_tweet['text'].split()[-1].translate(str.maketrans({'「': '', '」': ''}))
        print(theme)
        if '@' in theme or len(theme) > 30:
            continue
        for _ in range(10):
            seed = random.randint(0, 100000)
            print(f"seed:{seed}")
            try:
                story_list = generate_story_list(theme, seed, stage_max)
                first_tweet_info = tweet_story(story_list)
                reply_text = f"@{call_tweet['user']['screen_name']}\nネタを投稿しました！\n" \
                             f"https://twitter.com/milkboy_core_ai/status/{first_tweet_info['id']}"
                update_status(reply_text, call_tweet['id_str'])
                print("ツイート成功")
                break
            except FailError as e:
                print(e)
                continue
        else:
            reply_text = f"@{call_tweet['user']['screen_name']}\n申し訳ありません。そのテーマではネタを作れませんでした。\n"
            update_status(reply_text, call_tweet['id_str'])
            continue
