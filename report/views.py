from django.shortcuts import render,render_to_response
from crawl import *
from report.models import *
from django.http.response import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from forms import *
# Create your views here.
def scrapper(request):     # all report crawl
    scrappe()
                
    return HttpResponse("crawl success")
def index(request):
        results =result.objects.all()
        summarys= summary.objects.all().last()  
        if request.method == "POST":
            key = request.POST['key']
            title =  result.objects.filter(title__contains=key)
            return render(request,'search.html',locals())
        return render(request, 'index.html', locals())
        
def report(request,id):
        results =result.objects.filter(report_id=id)
        dialogues = dialogue.objects.filter(report_id=id)        
        summaries = summar.objects.filter(report_id=id)
        return render_to_response("report.html",locals()) 
def updates(request):
    update()
    summary1= summary.objects.all().last() 
    summary2= summary.objects.all().order_by('-pk')[1:2]
    return render_to_response("update.html",locals()) 