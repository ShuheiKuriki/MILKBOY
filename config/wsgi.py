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
from milkboy.views import GENRES
from milkboy.coreAI import generate_neta_list
from twitter import Twitter, TwitterStream, OAuth

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

application = get_wsgi_application()


def get_auth():
    try:
        from config.settings import dev
        auth = OAuth(
            dev.TW_TOKEN,
            dev.TW_TOKEN_SECRET,
            dev.TW_CONSUMER_KEY,
            dev.TW_CONSUMER_SECRET
        )
        print('this is from dev')
    except:
        from config.settings import prod
        auth = OAuth(
            prod.TW_TOKEN,
            prod.TW_TOKEN_SECRET,
            prod.TW_CONSUMER_KEY,
            prod.TW_CONSUMER_SECRET
        )
        print('this is from prod')
    return auth


def tweet():
    api = Twitter(auth=get_auth())
    res = 'fail'
    while res != 'success':
        time.sleep(10)
        start_t = time.time()
        stage_max = 3
        genre_name = random.choice(GENRES + ['random']*3)
        print(genre_name)
        theme = pred1 = pred2 = ''
        first_stage = {}
        neta_list = []
        stage_num = 3
        while True:
            try:
                seed = random.randint(0, 100000)
                if genre_name == 'random':
                    neta_list = generate_neta_list('random', seed, stage_max)
                else:
                    neta_list = generate_neta_list('', seed, stage_max, genre_name)
                stage_num = len(neta_list)
                if time.time() - start_t > 30:
                    continue
            except:
                continue
            first_stage = neta_list[0] if stage_num > 1 else neta_list[-1]
            theme = first_stage['theme']
            pred1, pred2 = first_stage['pred1'], first_stage['pred2']
            if pred1 != '' and pred2 != '':
                break
        # つかみ
        text1, text2 = tsukami_script(theme, first_stage['tsukami'])
        data = update_status(api, text1)
        data = update_status(api, text2, data['id'])
        # 導入
        text1, text2, text3 = introduction(first_stage['category'], pred1, pred2)
        data = update_status(api, text1, data['id'])
        data = update_status(api, text2, data['id'])
        data = update_status(api, text3, data['id'])

        for i in range(stage_num):
            neta = neta_list[i] if i < stage_num-1 else neta_list[-1]
            feat = f"駒場「{neta['featX']}」"
            data = update_status(api, feat, data['id'])
            feat_reply = f"内海「{neta['featX_reply']}」"
            data = update_status(api, feat_reply, data['id'])

            anti_feat = f"駒場「{neta['anti_featX']}」"
            data = update_status(api, anti_feat, data['id'])
            anti_feat_reply = f"内海「{neta['anti_featX_reply']}」"
            data = update_status(api, anti_feat_reply, data['id'])

            if i == stage_num-2:
                continue
            text = f"駒場「{neta['conjunction']}」"
            if i == stage_num-1:
                text += "\n\n内海「いや、絶対ちゃうやろ。」\n\n"
                text += "内海「もうええわ、どうもありがとうございました。」"
            data = update_status(api, text, data['id'])
        print('last of tweet func')
        res = 'success'
    print(res)
    return


def auto_reply():
    api = Twitter(auth=get_auth())
    twitter_stream = TwitterStream(auth=get_auth())
    theme = pred1 = pred2 = ''
    first_stage = {}
    neta_list = []
    stage_num = 3
    print('activate auto reply')
    for tweet in twitter_stream.statuses.filter(language='ja', track='@milkboy_core_ai テーマ'):
        start_t = time.time()
        stage_max = 3
        print(tweet)
        try:
            theme = tweet['text'].split()[-1]
            if '@' in theme or len(theme) > 30:
                continue
            tle = False
            while True:
                try:
                    seed = random.randint(0, 100000)
                    neta_list = generate_neta_list(theme, seed, stage_max)
                    stage_num = len(neta_list)
                    if time.time() - start_t > 30:
                        tle = True
                        break
                except:
                    continue
                first_stage = neta_list[0] if stage_num > 1 else neta_list[-1]
                pred1, pred2 = first_stage['pred1'], first_stage['pred2']
                print(pred1)
                if pred1 != '' and pred2 != '':
                    break
            if tle:
                continue
            # つかみ
            text1, text2 = tsukami_script(theme, first_stage['tsukami'])
            first_tweet = update_status(api, text1)
            data = update_status(api, text2, first_tweet['id'])
            # 導入
            text1, text2, text3 = introduction(first_stage['category'], pred1, pred2)
            data = update_status(api, text1, data['id'])
            data = update_status(api, text2, data['id'])
            data = update_status(api, text3, data['id'])

            for i in range(stage_num):
                neta = neta_list[i] if i < stage_num - 1 else neta_list[-1]
                feat = f"駒場「{neta['featX']}」"
                data = update_status(api, feat, data['id'])
                feat_reply = f"内海「{neta['featX_reply']}」"
                data = update_status(api, feat_reply, data['id'])

                anti_feat = f"駒場「{neta['anti_featX']}」"
                data = update_status(api, anti_feat, data['id'])
                anti_feat_reply = f"内海「{neta['anti_featX_reply']}」"
                data = update_status(api, anti_feat_reply, data['id'])

                if i == stage_num - 2:
                    continue
                text = f"駒場「{neta['conjunction']}」"
                if i == stage_num - 1:
                    text += "\n\n内海「いや、絶対ちゃうやろ。」\n\n"
                    text += "内海「もうええわ、どうもありがとうございました。」"
                data = update_status(api, text, data['id'])
            reply_text = f"@{tweet['user']['screen_name']}\nネタを投稿しました！\n"
            reply_text += f"https://twitter.com/milkboy_core_ai/status/{first_tweet['id']}"
            update_status(api, reply_text, tweet['id_str'])
        except:
            continue


def update_status(api, tweet_text, reply_id=None):
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
        data = api.statuses.update(status=texts[0])
    else:
        data = api.statuses.update(status=texts[0], in_reply_to_status_id=reply_id)
    for text in texts[1:]:
        data = api.statuses.update(status=text, in_reply_to_status_id=data['id'])
    return data


def tsukami_script(word, tsukami):
    dt_now = datetime.datetime.now()
    text = dt_now.strftime('%m月%d日 %H:%M:%S') + "\n\n"
    text += f"テーマ: {word}\n\n"
    text += "内海「どうもーミルクボーイです。お願いします。」\n\n"

    text2 = "内海「あーありがとうございますー。"
    if len(tsukami) >= 10:
        text2 += 'ね、今、[' + tsukami + ']をいただきましたけどもね。'
        text2 += 'こんなんなんぼあっても良いですからね、'
    else:
        text2 += 'ね、今、何もいただけませんでしたけどもね。'
        text2 += '何ももらえなくてもね、聞いてもらえるだけ'
    text2 += 'ありがたいですよ。いうとりますけどもね。」\n'
    return text, text2


def introduction(category, pred1, pred2):
    text = '駒場「うちのおかんがね、好きな[' + category + ']があるらしいんやけど、その名前をちょっと忘れたらしくてね。」\n\n'
    text += '内海「好きな[' + category + ']忘れてもうて。どうなってんねんそれ。'

    text2 = '内海「ほんでもおかんが好きな[' + category + ']なんて、[' + pred1 + ']か[' + pred2 + ']くらいでしょう。」\n\n'
    text2 += '駒場「それが違うらしいねんな」'

    text3 = '内海「ほんだら俺がね、おかんの好きな[' + category + ']一緒に考えてあげるから、どんな特徴言うてたかとか教えてみてよ。」'
    return text, text2, text3


def always():
    schedule.every().day.at("09:00").do(tweet)
    schedule.every().day.at("12:00").do(tweet)
    schedule.every().day.at("15:00").do(tweet)
    schedule.every().day.at("18:00").do(tweet)
    schedule.every().day.at("21:00").do(tweet)
    schedule.every().day.at("00:00").do(tweet)
    while True:
        for i in range(9):
            schedule.run_pending()
            time.sleep(1200)
            req = requests.get("https://www.milkboy-core-ai.tech")
            print('successfully accessed' if req.status_code == requests.codes.ok else 'access failed')


t = threading.Thread(target=always)
t2 = threading.Thread(target=auto_reply)
t.start()
t2.start()
