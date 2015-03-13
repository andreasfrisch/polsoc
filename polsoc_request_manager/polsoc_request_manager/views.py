from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.utils.dateformat import format
from polsoc_request_manager.models import PolsocRequest, PolsocRequestForm
from polsoc_request_manager.settings import OUTPUT_FOLDER

import logging
polsoc_logger = logging.getLogger("polsoc")

def generateFilenameFromForm(form):
    return "stub"
    #return "%s/%s_[%s-%s]" % (OUTPUT_FOLDER, form.query_name, form.from_date, form.to_date)

def home(request):
    if request.method == "POST":
        form = PolsocRequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.filename = generateFilenameFromForm(form)
            new_request.save()
            return redirect("home")            
        else:
            #TODO Handle it!
            return redirect("home")
    else:
        context = {}
        context["requests"] = PolsocRequest.objects.all()
        context["requestForm"] = PolsocRequestForm()
        return render(request, "home.html", context)

def serveFile(request, request_id):
    polsoc_request = None
    try:
        polsoc_request = PolsocRequest.objects.get(id=request_id)
    except Exception as error:
        polsoc_logger("Couldn't find PolsocRequest with Id %s: %s" % (request_id, error))
        return HttpResponse(500)
    polsoc_request.has_been_downloaded = True
    polsoc_request.save()
    # TODO: actually serve the file
    return HttpResponse(200)

def transformRequestToJson(request):
    return {
        "id": request.id,
        "filename": request.filename,
        "facebook_id": request.facebook_id,
        "facebook_access_token": request.facebook_access_token,
        "from_date": request.from_date,
        "to_date": request.to_date,
        "include_comments": request.include_comments
    }

def getNextInQueue(request):
    next_request = PolsocRequest.objects.filter(has_been_processed=False)[0]
    return JsonResponse(transformRequestToJson(next_request), safe=False)
    
def markAsCompleted(request, request_id):
    request_object = None
    try:
        request_object = PolsocRequest.objects.get(id=request_id)
    except Exception as error:
        polsoc_logger("Couldn't find PolsocRequest with Id %s: %s" % (request_id, error))
        return HttpResponse(500)
    request_object.has_been_processed = True
    request_object.save()
    return HttpResponse(200)
    
def getDownloadedRequests(request):
    downloaded_requests = PolsocRequest.objects.filter(has_been_downloaded=True)
    return JsonResponse(map(transformRequestToJson, downloaded_requests), safe=False)

def markAsRemoved(request, request_id):
    request_object = None
    try:
        request_object = PolsocRequest.objects.get(id=request_id)
    except Exception as error:
        polsoc_logger("Couldn't find PolsocRequest with Id %s: %s" % (request_id, error))
        return HttpResponse(500)
    request_object.delete()
    return HttpResponse(200)