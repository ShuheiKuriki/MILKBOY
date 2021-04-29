# from django.shortcuts import render
from django.views.generic import TemplateView
from django.http.response import JsonResponse
from .coreAI import generate_neta_list
from collections import defaultdict
GLOBAL_DICTS = defaultdict(lambda: {})

class IndexView(TemplateView):
    template_name = 'index.html'
# Create your views here.

def stage(request):
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

    return JsonResponse(GLOBAL_DICTS[k][data['stage']])
