# Create your views here.
from django.template.loader import get_template
from django.template import RequestContext
from django.http import HttpResponse
from no3z_www.main.models import Noticia
from no3z_www.create import get_context
import random

def main(request):
    noticia = Noticia.objects.order_by('?')
    temp = get_template('template.html')
    context_table = {'all' : noticia[:30],}
    html = temp.render(RequestContext(request,context_table))
    return HttpResponse(html)

def music(request):
    noticia = Noticia.objects.filter(music__contains='media/uploads/music/')
    noticia = noticia.order_by('?')
    temp = get_template('template.html')
    context_table = {'all' : noticia[:30],}
    html = temp.render(RequestContext(request,context_table))
    return HttpResponse(html)

def news(request):
    noticia = Noticia.objects.filter(music__isnull=True)
    noticia = noticia.order_by('?')
    temp = get_template('template.html')
    context_table = {'all' : noticia[:30],}
    html = temp.render(RequestContext(request,context_table))
    return HttpResponse(html)

def getfeeds(request):
    get_context()
    return 0