"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import time
import datetime
import random
import schedule
import threading
import requests

from django.core.wsgi import get_wsgi_application
from milkboy.coreAI import generate_story_list
from twitter import Twitter, TwitterStream, OAuth

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

application = get_wsgi_application()

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
    for _ in range(v):
        GENRES.append(k)


def get_auth():
    try:
        from config.settings import prod
        auth = OAuth(
            prod.TW_TOKEN,
            prod.TW_TOKEN_SECRET,
            prod.TW_CONSUMER_KEY,
            prod.TW_CONSUMER_SECRET
        )
        print('import prod settings file')
    except KeyError:
        from config.settings import dev
        auth = OAuth(
            dev.TW_TOKEN,
            dev.TW_TOKEN_SECRET,
            dev.TW_CONSUMER_KEY,
            dev.TW_CONSUMER_SECRET
        )
        print('import dev settings file')
    return auth


def tweet_story():
    res = 'start tweet'
    print(res)
    while res != 'tweet success':
        time.sleep(10)
        stage_max = 5
        genre_name = random.choice(GENRES)
        print(genre_name)
        theme = prediction1 = prediction2 = ''
        first_stage = {}
        stage_num = 0
        while True:
            start_t = time.time()
            seed = random.randint(0, 100000)
            if genre_name == 'random':
                story_list = generate_story_list('random', seed, stage_max)
            else:
                story_list = generate_story_list('', seed, stage_max, genre_name)
            if story_list is False:
                continue
            stage_num = len(story_list)
            if time.time() - start_t > 30:
                continue
            first_stage = story_list[0] if stage_num > 1 else story_list[-1]
            theme = first_stage['theme']
            prediction1, prediction2 = first_stage['prediction1'], first_stage['prediction2']
            if prediction1 != '' and prediction2 != '':
                break
        # つかみ
        text1, text2 = present_script(theme, first_stage['present'])
        first_tweet = update_status(text1)
        data = update_status(text2, first_tweet['id'])
        # 導入
        texts = introduction(first_stage['category'], prediction1, prediction2)
        data = multiple_tweets(texts, data)
        for i in range(stage_num):
            story = story_list[i] if i < stage_num - 1 else story_list[-1]
            feat_text = [f"駒場「{story['featX']}」\n\n", f"内海「{story['featX_reply']}」\n\n",
                         f"駒場「{story['anti_featX']}」\n\n", f"内海「{story['anti_featX_reply']}」\n\n"]
            if i != stage_num - 2:
                feat_text.append(f"駒場「{story['conjunction']}」\n\n")
            if i == stage_num - 1:
                feat_text.append("内海「いや、絶対ちゃうやろ。」\n\n")
                feat_text.append("内海「もうええわ、どうもありがとうございました。」\n\n")
            data = multiple_tweets(feat_text, data)
        print('last of tweet func')
        res = 'tweet success'
    print(res)
    return


def auto_reply():
    twitter_stream = TwitterStream(auth=get_auth())
    prediction1 = prediction2 = ''
    first_stage = {}
    print('activate auto reply')
    for tweet in twitter_stream.statuses.filter(language='ja', track='@milkboy_core_ai テーマ'):
        stage_max = 5
        stage_num = 0
        story_list = []
        print(f"リプライツイートアカウント名：{tweet['user']['name']}")
        print(f"ツイート内容：{tweet['text']}")
        theme = tweet['text'].split()[-1].translate(str.maketrans({'「': '', '」': ''}))
        print(theme)
        if '@' in theme or len(theme) > 30:
            continue
        for _ in range(10):
            seed = random.randint(0, 100000)
            print(f"seed:{seed}")
            story_list = generate_story_list(theme, seed, stage_max)
            if story_list is False:
                continue
            stage_num = len(story_list)
            first_stage = story_list[0] if stage_num > 1 else story_list[-1]
            prediction1, prediction2 = first_stage['prediction1'], first_stage['prediction2']
            print(prediction1, prediction2)
            if prediction1 != '' and prediction2 != '':
                break
        else:
            reply_text = f"@{tweet['user']['screen_name']}\n申し訳ありません。そのテーマではネタを作れませんでした。\n"
            update_status(reply_text, tweet['id_str'])

        # つかみ
        text1, text2 = present_script(theme, first_stage['present'])
        first_tweet = update_status(text1)
        data = update_status(text2, first_tweet['id'])
        # 導入
        texts = introduction(first_stage['category'], prediction1, prediction2)
        data = multiple_tweets(texts, data)
        for i in range(stage_num):
            story = story_list[i] if i < stage_num - 1 else story_list[-1]
            feat_text = [f"駒場「{story['featX']}」\n\n", f"内海「{story['featX_reply']}」\n\n",
                         f"駒場「{story['anti_featX']}」\n\n", f"内海「{story['anti_featX_reply']}」\n\n"]
            if i != stage_num - 2:
                feat_text.append(f"駒場「{story['conjunction']}」\n\n")
            if i == stage_num - 1:
                feat_text.append("内海「いや、絶対ちゃうやろ。」\n\n")
                feat_text.append("内海「もうええわ、どうもありがとうございました。」\n\n")
            data = multiple_tweets(feat_text, data)
        reply_text = f"@{tweet['user']['screen_name']}\nネタを投稿しました！\n"
        reply_text += f"https://twitter.com/milkboy_core_ai/status/{first_tweet['id']}"
        update_status(reply_text, tweet['id_str'])
        print("ツイート成功")


def multiple_tweets(texts, data):
    text = ''
    for tweet_text in texts:
        if len(text + tweet_text) <= 130:
            text += tweet_text
        elif len(text) == 0:
            data = update_status(tweet_text, data['id'])
        else:
            data = update_status(text, data['id'])
            text = tweet_text
    data = update_status(text, data['id'])
    return data


def update_status(tweet_text, reply_id=None):
    max_len = 130
    texts = []
    if len(tweet_text) > max_len:
        left = 0
        right = max_len
        texts.append(tweet_text[left:right])
        while right < len(tweet_text):
            left += max_len
            right += max_len
            texts.append(tweet_text[left:right])
    else:
        texts.append(tweet_text)
    if reply_id is None:
        data = API.statuses.update(status=texts[0])
    else:
        data = API.statuses.update(status=texts[0], in_reply_to_status_id=reply_id)
    for text in texts[1:]:
        data = API.statuses.update(status=text, in_reply_to_status_id=data['id'])
    return data


def present_script(word, present):
    dt_now = datetime.datetime.now()
    text = dt_now.strftime('%m月%d日 %H:%M:%S') + "\n\n"
    text += f"テーマ: {word}\n\n"
    text += "内海「どうもーミルクボーイです。お願いします。」\n\n"

    text2 = "内海「あーありがとうございますー。"
    if len(present) >= 10:
        text2 += 'ね、今、[' + present + ']をいただきましたけどもね。'
        text2 += 'こんなんなんぼあっても良いですからね、'
    else:
        text2 += 'ね、今、何もいただけませんでしたけどもね。'
        text2 += '何ももらえなくてもね、聞いてもらえるだけ'
    text2 += 'ありがたいですよ。いうとりますけどもね。」\n\n'
    return text, text2


def introduction(category, prediction1, prediction2):
    text = '駒場「うちのおかんがね、好きな[' + category + ']があるらしいんやけど、その名前をちょっと忘れたらしくてね。」\n\n'
    text += '内海「好きな[' + category + ']忘れてもうて。どうなってんねんそれ。\n\n'

    text2 = '内海「ほんでもおかんが好きな[' + category + ']なんて、[' + prediction1 + ']か[' + prediction2 + ']くらいでしょう。」\n\n'
    text2 += '駒場「それが違うらしいねんな」\n\n'

    text3 = '内海「ほんだら俺がね、おかんの好きな[' + category + ']一緒に考えてあげるから、どんな特徴言うてたかとか教えてみてよ。」\n\n'
    return text, text2, text3


def daily():
    schedules = ["09:00", "12:00", "15:00", "18:00", "21:00"]
    for tweet_time in schedules:
        schedule.every().day.at(tweet_time).do(tweet_story)
    while True:
        schedule.run_pending()
        time.sleep(1200)
        req = requests.get("https://www.milkboy-core-ai.tech")
        print('successfully accessed' if req.status_code == requests.codes.ok else 'access failed')


def always():
    while True:
        auto_reply()


API = Twitter(auth=get_auth())
t = threading.Thread(target=daily)
t2 = threading.Thread(target=always)
t.start()
t2.start()
