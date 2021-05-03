from django.shortcuts import render
from django.views.generic import TemplateView

def index(request):
    genres = ['日本の映画', '日本の漫画', 'アニメ', '日本のゲーム', '日本の歴史', '日本の地理', '日本のスポーツ', '日本の音楽',
              '物質', '物理現象', '数学的対象', '計算機科学', 'アルゴリズムとデータ構造']
    return render(request, 'index.html', {'genres': genres})
# Create your views here.
