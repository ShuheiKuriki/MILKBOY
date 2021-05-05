import os
import random
import time
import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from .coreAI import generate_neta_list
from collections import defaultdict
from twitter import Twitter, TwitterStream, OAuth
GLOBAL_DICTS = defaultdict(lambda: {})

GENRES = ['日本の映画', '日本の漫画', 'アニメ', '日本のゲーム', '日本の歴史', '日本の地理', '日本のスポーツ', '日本の音楽',
          '物質', '物理現象', '数学的対象', '計算機科学', 'アルゴリズムとデータ構造']


def index(request):
    return render(request, 'index.html', {'genres': GENRES})


def theme(request):
    data = {
        "input_theme": request.GET.get("input_theme"),
        "seed": int(request.GET.get("seed")),
        "stage": int(request.GET.get("stage")),
        "stage_max": int(request.GET.get("stage_max"))
    }

    k = (data['input_theme'], data['seed'], data['stage_max'])
    if k not in GLOBAL_DICTS or data['stage'] not in GLOBAL_DICTS[k]:
        # ネタを作る
        result_list = generate_neta_list(data['input_theme'], data['seed'], data['stage_max'])

        if len(result_list) == 1:
            return JsonResponse(result_list[0])

        for result in result_list:
            GLOBAL_DICTS[(data['input_theme'], data['seed'], data['stage_max'])][result['stage']] = result
    print(GLOBAL_DICTS[k][data['stage']])
    return JsonResponse(GLOBAL_DICTS[k][data['stage']])


def genre(request):
    data = {
        "genre": request.GET.get("genre"),
        "seed": int(request.GET.get("seed")),
        "stage": int(request.GET.get("stage")),
        "stage_max": int(request.GET.get("stage_max")),
    }

    k = (data['genre'], data['seed'], data['stage_max'])
    if k not in GLOBAL_DICTS or data['stage'] not in GLOBAL_DICTS[k]:
        result_list = generate_neta_list('', data['seed'], data['stage_max'], data['genre'])
        if len(result_list) == 1:
            return JsonResponse(result_list[0])

        for result in result_list:
            GLOBAL_DICTS[(data['genre'], data['seed'], data['stage_max'])][result['stage']] = result
    print(GLOBAL_DICTS[k][data['stage']])
    return JsonResponse(GLOBAL_DICTS[k][data['stage']])


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


def tweet(request):
    api = Twitter(auth=get_auth())
    start_t = time.time()
    stage_max = 3
    genre_name = random.choice(GENRES + ['random']*5)
    print(genre_name)
    while True:
        try:
            seed = random.randint(0, 100000)
            if genre_name == 'random':
                neta_list = generate_neta_list('random', seed, stage_max)
            else:
                neta_list = generate_neta_list('', seed, stage_max, genre_name)
            stage_num = len(neta_list)
            if time.time() - start_t > 15:
                return HttpResponse('')
        except:
            continue
        first_stage = neta_list[0] if stage_num > 1 else neta_list[-1]
        pred1, pred2 = first_stage['pred1'], first_stage['pred2']
        if pred1 != '' and pred2 != '':
            break
    # つかみ
    text1, text2 = tsukami_script(genre_name, first_stage['tsukami'])
    data = api.statuses.update(status=text1)
    data = api.statuses.update(status=text2, in_reply_to_status_id=data['id'])
    # 導入
    text1, text2, text3 = introduction(first_stage['category'], pred1, pred2)
    data = api.statuses.update(status=text1, in_reply_to_status_id=data['id'])
    data = api.statuses.update(status=text2, in_reply_to_status_id=data['id'])
    data = api.statuses.update(status=text3, in_reply_to_status_id=data['id'])

    for i in range(stage_num):
        neta = neta_list[i] if i < stage_num-1 else neta_list[-1]
        feat = f"駒場「{neta['featX']}」"
        data = api.statuses.update(status=feat, in_reply_to_status_id=data['id'])
        feat_reply = f"内海「{neta['featX_reply']}」"
        data = api.statuses.update(status=feat_reply, in_reply_to_status_id=data['id'])

        anti_feat = f"駒場「{neta['anti_featX']}」"
        data = api.statuses.update(status=anti_feat, in_reply_to_status_id=data['id'])
        anti_feat_reply = f"内海「{neta['anti_featX_reply']}」"
        data = api.statuses.update(status=anti_feat_reply, in_reply_to_status_id=data['id'])

        if i == stage_num-2:
            continue
        text = f"駒場「{neta['conjunction']}」"
        if i == stage_num-1:
            text += "\n\n内海「いや、絶対ちゃうやろ。」\n\n"
            text += "内海「もうええわ、どうもありがとうございました。」"
        data = api.statuses.update(status=text, in_reply_to_status_id=data['id'])
    print('last of tweet func')
    return HttpResponse('')


def auto_reply():
    api = Twitter(auth=get_auth())
    twitter_stream = TwitterStream(auth=get_auth())
    for tweet in twitter_stream.statuses.filter(language='ja', track='@milkboy_core_ai テーマ'):
        start_t = time.time()
        stage_max = 3
        theme = tweet['text'].split()[-1]
        if '@' in theme or len(theme) > 10:
            return HttpResponse('')
        while True:
            try:
                seed = random.randint(0, 100000)
                neta_list = generate_neta_list(theme, seed, stage_max)
                stage_num = len(neta_list)
                if time.time() - start_t > 15:
                    return HttpResponse('')
            except:
                continue
            first_stage = neta_list[0] if stage_num > 1 else neta_list[-1]
            pred1, pred2 = first_stage['pred1'], first_stage['pred2']
            if pred1 != '' and pred2 != '':
                break
        # つかみ
        text1, text2 = tsukami_script('', first_stage['tsukami'])
        data = api.statuses.update(status=text1, in_reply_to_status_id=tweet['id_str'])
        data = api.statuses.update(status=text2, in_reply_to_status_id=data['id'])
        # 導入
        text1, text2, text3 = introduction(first_stage['category'], pred1, pred2)
        data = api.statuses.update(status=text1, in_reply_to_status_id=data['id'])
        data = api.statuses.update(status=text2, in_reply_to_status_id=data['id'])
        data = api.statuses.update(status=text3, in_reply_to_status_id=data['id'])

        for i in range(stage_num):
            neta = neta_list[i] if i < stage_num - 1 else neta_list[-1]
            feat = f"駒場「{neta['featX']}」"
            data = api.statuses.update(status=feat, in_reply_to_status_id=data['id'])
            feat_reply = f"内海「{neta['featX_reply']}」"
            data = api.statuses.update(status=feat_reply, in_reply_to_status_id=data['id'])

            anti_feat = f"駒場「{neta['anti_featX']}」"
            data = api.statuses.update(status=anti_feat, in_reply_to_status_id=data['id'])
            anti_feat_reply = f"内海「{neta['anti_featX_reply']}」"
            data = api.statuses.update(status=anti_feat_reply, in_reply_to_status_id=data['id'])

            if i == stage_num - 2:
                continue
            text = f"駒場「{neta['conjunction']}」"
            if i == stage_num - 1:
                text += "\n\n内海「いや、絶対ちゃうやろ。」\n\n"
                text += "内海「もうええわ、どうもありがとうございました。」"
            data = api.statuses.update(status=text, in_reply_to_status_id=data['id'])
        return HttpResponse('')


def tsukami_script(genre_name, tsukami):
    dt_now = datetime.datetime.now()
    text = dt_now.strftime('%m月%d日 %H:%M:%S') + "\n\n"
    if genre_name != '':
        text += f"ジャンル: {genre_name}\n\n"
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
