from django.shortcuts import render
from django.http.response import JsonResponse
from .coreAI import generate_story_list
from collections import defaultdict
from pprint import pprint

GLOBAL_DICTS = defaultdict(lambda: {})

GENRES = ['日本の映画', '日本の漫画', 'アニメ', '日本のゲーム', '日本の歴史', '日本の地理', '日本のスポーツ', '日本の音楽', '日本語の語句',
          '日本の人物_(分野別)', '日本の人物_(職業別)', '物質', '物理現象', '数学的対象', '計算機科学', 'アルゴリズムとデータ構造']


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
        result_list = generate_story_list(data['input_theme'], data['seed'], data['stage_max'])

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
        result_list = generate_story_list('', data['seed'], data['stage_max'], data['genre'])
        print(f"ネタの長さ：{len(result_list)}")
        if len(result_list) == 1:
            result = result_list[0]
            GLOBAL_DICTS[k][result['stage']] = result
            return JsonResponse(result)

        for result in result_list:
            GLOBAL_DICTS[k][result['stage']] = result

    pprint(GLOBAL_DICTS[k][data['stage']])

    return JsonResponse(GLOBAL_DICTS[k][data['stage']])
