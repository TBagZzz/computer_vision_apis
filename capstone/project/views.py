import os
import random
import tempfile
from django.http import JsonResponse
from django.shortcuts import render
import json
import time as processTiming
from datetime import timedelta,datetime,time,date
from . import models, vision_helper
from rest_framework.decorators import api_view
from .vision_helper import Vision
from .bcard_nlp import NLP
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage


# Create your views here.
"""[NLP tranform text after the natural language processing]

Returns:
    [type] -- [description]
"""

# def trial(request):
# 	return(render(request,"trial.html"))


def nlp(request):
    query = request.GET.get('query', '')
    data = ""
    if(query):
        data = dialog_flow(query)
    resp = {"status":200,"data":data}
    return JsonResponse(resp)


#-----------------------
#VISION API
#-----------------------
@csrf_exempt
@api_view(['POST'])
def upload_client(request):
    startTime = processTiming.time()
    try :
        temporary_file = tempfile.NamedTemporaryFile()
        uploaded_file = request.FILES['document']
        temporary_file.write(uploaded_file.file.read())
        temporary_file.flush()

        file = request.data.get("document", "")
        currentTime = datetime.now()
        file_name = file.name
        
        txt = request.query_params.get("type","")
        obj = Vision(temporary_file.name)
        if txt == "brand": 
            logo_D = obj.detect_logo()
            task = "Brand_detection"
            result = logo_D

        elif txt == "text":
            text_D = obj.detect_text()     
            task = "Text_detection"
            result = text_D

        elif txt == "label":
            label = obj.provideLabel()
            task = "Label_Image"
            result = label
        
        #Working on beta from vision_helper.py
        elif txt == "visiting_card":
            details = obj.detect_text_card_beta()
            task = "business_card"
            result = details
            JsonObj = {"Objective" : "Image_Upload",
                "Upload_status" : "Success",
                "File_Name" : file_name,
                "Upload_Time" : currentTime,
                "Task" : task}
            for elem in result:
                jsonAddition = {elem[0] : elem[1]}
                JsonObj.update(jsonAddition)
            timeSpan = {"Time_Stamp" : "{} seconds".format(float(round(processTiming.time() - startTime,2)))}
            JsonObj.update(timeSpan)
            return JsonResponse(JsonObj)

        else:
            return JsonResponse({"ERROR" : "Wrong Query"})
        return JsonResponse({"Objective" : "Image_Upload",
            "Upload_status" : "Success",
            "File_Name" : file_name,
            "Upload_Time" : currentTime,
            "Task" : task,
            "Result" : result,
            "Time_Stamp" : "{} seconds".format(float(round(processTiming.time() - startTime,2)))})
    except (KeyError):
        return JsonResponse({"Upload status" : "Failed"})



#BETA

# @api_view(['GET'])
# def LabelWikia_client(request):
#     startTime = processTiming.time()
#     try :
#         temporary_file = tempfile.NamedTemporaryFile()
#         uploaded_file = request.FILES['document']
#         temporary_file.write(uploaded_file.file.read())
#         temporary_file.flush()

#         file = request.data.get("document", "")
#         currentTime = datetime.now()
#         file_name = file.name
        
#         txt = request.query_params.get("type","")
#         obj = Vision(temporary_file.name)

#         if txt == "wiki":
#         	wiki = obj.provideLabel()
#         	task = "Wiki of Object (Beta)"
#         	result = wiki.WikiDetails()

#         else:
#             return JsonResponse({"ERROR" : "Wrong Query"})
#         return JsonResponse({"Objective" : "Image_Upload",
#             "Upload_status" : "Success",
#             "File_Name" : file_name,
#             "Upload_Time" : currentTime,
#             "Task" : task,
#             "Result" : result,
#             "Time_Stamp" : "{} seconds".format(float(round(processTiming.time() - startTime,2)))})
#     except (KeyError):
#         return JsonResponse({"Upload status" : "Failed"})


# -----------------------
