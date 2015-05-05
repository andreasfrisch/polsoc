from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.utils.dateformat import format
from polsoc_request_manager.models import PolsocRequest, PolsocRequestForm
from polsoc_request_manager.settings import OUTPUT_FOLDER
from django.views.decorators.csrf import csrf_exempt

import logging
polsoc_logger = logging.getLogger("polsoc")

def generateFilenameFromForm(form):
    return "%s/%s_[%s-%s].csv" % (OUTPUT_FOLDER, form["query_name"], form["from_date"].replace('/','.'), form["to_date"].replace('/','.'))

@csrf_exempt
def home(request):
    polsoc_logger.debug("HOME REACHED")
    if request.method == "POST":
        polsoc_logger.debug("POST for new request")
        form = PolsocRequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.filename = generateFilenameFromForm(request.POST)
            new_request.save()
            return redirect("home")            
        else:
            #TODO Handle it!
            polsoc_logger.debug("INVALID FORM")
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
        polsoc_logger.debug("Couldn't find PolsocRequest with Id %s: %s" % (request_id, error))
        return HttpResponse(500)
    polsoc_request.has_been_downloaded = True
    polsoc_request.save()

    fsock = open(polsoc_request.filename, 'r')
    response = HttpResponse(fsock, content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=%s.csv" % polsoc_request.query_name
    return response

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
    next_request = None
    if (len(PolsocRequest.objects.filter(process_state=1)) == 0):
        unprocessed = PolsocRequest.objects.filter(process_state=0)
        if len(unprocessed) > 0:
            next_request = unprocessed[0]
            next_request.processed_state = 1
            next_request.save()
    if next_request:
        return JsonResponse(transformRequestToJson(next_request), safe=False)
    return None
    
def markAsCompleted(request, request_id):
    request_object = None
    try:
        request_object = PolsocRequest.objects.get(id=request_id)
    except Exception as error:
        polsoc_logger.debug("Couldn't find PolsocRequest with Id %s: %s" % (request_id, error))
        return HttpResponse(500)
    request_object.process_state = 2
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
        polsoc_logger.debug("Couldn't find PolsocRequest with Id %s: %s" % (request_id, error))
        return HttpResponse(500)
    request_object.delete()
    return HttpResponse(200)
