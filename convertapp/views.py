from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.http.response import JsonResponse
import json
import  os
import pandas as pd
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process
from django.utils import *
from django.templatetags.static import static
from Convert.settings import BASE_DIR
from django.core.files.base import File
from django.conf import settings as django_settings
import numpy as np
import re
import mimetypes
from django.core.files import File



from .utils import *



client_filename = ""
client_filename_modified = ""
sanveo_filename = ""
dict_filename = ""
output_dictionary = ""
output_filename = ""
output_filename_multiple = ""
dictionary_applied = False


UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/files")

OUTPUT_FOLDER = os.path.join(BASE_DIR, "static/outputs")

OUTPUT_DICT_FOLDER = os.path.join(BASE_DIR, "static/dict_output")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
if not os.path.exists(OUTPUT_DICT_FOLDER):
    os.makedirs(OUTPUT_DICT_FOLDER)



from werkzeug.utils import secure_filename



ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def home(request):

    return render(request, "index.html")
    #return HttpResponse('Home Page')


## function for uploading client file
def upload_client(request):
    global client_filename
	# check if the post request has the file part
    if 'source_fileName' not in request.FILES: ##change
        resp = JsonResponse({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
	
    files = request.FILES.getlist('source_fileName')
    errors = {}
    success = False
	
    for file in files:
        if file and allowed_file(file.name):  
            client_filename = "client.csv"

            path = os.path.join(UPLOAD_FOLDER, client_filename) 

            if os.path.exists(path):    
                os.remove(path)

            with open(path, 'wb') as dest:

                if file.multiple_chunks:
                    for c in file.chunks():  
                        dest.write(c)
                        break
                else:
                    dest.write(file.read())
                          
            success = True
            
        else:
            errors[file.name] = 'File type is not allowed' ###

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = JsonResponse(errors)
        resp.status_code = 206
        return resp
    if success:
        resp = JsonResponse({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = JsonResponse(errors)
        resp.status_code = 400
        return resp


## function for uploading sanveo reference file
def upload_sanveo(request):
    
    global sanveo_filename


	# check if the post request has the file part
    if 'source_fileName_Sanveo' not in request.FILES:
        resp = JsonResponse({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
	
    files = request.FILES.getlist('source_fileName_Sanveo')
	
    errors = {}
    success = False
	
    for file in files:
        if file and allowed_file(file.name):
            sanveo_filename = "sanveo.csv"
            path = os.path.join(UPLOAD_FOLDER, sanveo_filename)

            if os.path.exists(path):
                os.remove(path)

            with open(path, 'wb') as dest:
                if file.multiple_chunks:
                    for c in file.chunks():
                        dest.write(c)
                else:
                    dest.write(file.read())

            success = True
            
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = JsonResponse(errors)
        resp.status_code = 206
        return resp
    if success:
        resp = JsonResponse({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = JsonResponse(errors)
        resp.status_code = 400
        return resp



## function for uploading dictionary
def upload_dict(request):
    
    global dict_filename

	# check if the post request has the file part
    if 'source_fileName_Third' not in request.FILES:
        resp = JsonResponse({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
	
    files = request.FILES.getlist('source_fileName_Third')
	
    errors = {}
    success = False
	
    for file in files:
        if file and allowed_file(file.name):
            dict_filename = "client_dictionary.csv"
            path = os.path.join(UPLOAD_FOLDER, dict_filename)
            if os.path.exists(path):
                os.remove(path)

            with open(path, 'wb') as dest:
                if file.multiple_chunks:
                    for c in file.chunks():
                        dest.write(c)
                        break
                else:
                    dest.write(file.read())
                #file.save(path)
                success = True
            
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = JsonResponse(errors)
        resp.status_code = 206
        return resp
    if success:
        resp = JsonResponse({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = JsonResponse(errors)
        resp.status_code = 400
        return resp


def apply_dict(request):
    #check_msg= ""

    global dict_filename
    global output_dictionary
    global client_filename_modified

    global dictionary_applied

    dictionary_applied = True #if dictionary is applied, the process function will read client file differently

    resp = {}
    df_dict_work=[]

    dict_file_path = os.path.join(UPLOAD_FOLDER, dict_filename)

    ## Main processing function

    replacer = create_pattern(dict_file_path)

    print(f"*********Pattern Created**************")

    client_file = os.path.join(UPLOAD_FOLDER, client_filename)
    df_client = pd.read_csv(client_file)

    df_client_modified = df_client.applymap(lambda x : replacer.replace(x))

    client_filename_modified = "client_modified.csv"




    output_dictionary = "output" + "_" + "dictionary.csv"

    if os.path.exists(os.path.join(OUTPUT_DICT_FOLDER, client_filename_modified)):
        os.remove(os.path.join(OUTPUT_DICT_FOLDER, client_filename_modified))

    df_client_modified.to_csv(os.path.join(OUTPUT_DICT_FOLDER, client_filename_modified))

    msg = "Processing Finished"
    down_msg = "Download the output dict file"

    #resp['message_match'] = check_msg
    resp['message_finish'] = msg
    #resp['flag'] = 1
    resp['download_msg'] = down_msg

    #return resp
    return HttpResponse(json.dumps(resp), content_type="application/json")

def download_dict(request):
    global client_filename_modified
    path = os.path.join(OUTPUT_DICT_FOLDER, client_filename_modified)
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.csv")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    raise Http404


def processs(request):
    global client_filename
    global client_filename_modified
    global output_filename
    global dictionary_applied
    global output_filename_multiple

    check_msg= ""

    resp = {}
    ## Processing client and sanveo file

    if dictionary_applied:
        client_file_path = os.path.join(OUTPUT_DICT_FOLDER, client_filename_modified)
    else:
        client_file_path = os.path.join(UPLOAD_FOLDER, client_filename)


    print(f"{client_file_path}")
    df_client = pd.read_csv(client_file_path)


    sanveo_file = os.path.join(UPLOAD_FOLDER, sanveo_filename)
    df_sanveo = pd.read_csv(sanveo_file)


    tmp_cols = request.POST.getlist('sourceHeaderFieldsClient')
    selected_cols = tmp_cols[0].split(',')


    list_check = False
    print(f"Sanveo Availabe Columns \n\n")
    print(df_sanveo.columns)

    print(f"Client Availabe Columns\n\n")
    print(df_client.columns)
    for s in selected_cols:
        if s not in df_sanveo.columns:
            print(f"{s} not found!")
            list_check = True
    if list_check:
        check_msg = "Some column names didn't match"
        resp['message_match'] = check_msg
        resp['flag'] = 0
        return resp

    else:
        check_msg = "All column names matched"

    
    df_client_work = df_client[selected_cols].copy(deep=True)

    
    df_sanveo_work = df_sanveo[selected_cols].copy(deep=True)

    ## These feature engineerigs might be solved with dictionary. Need to be tested
    if "Size" in selected_cols:
        df_client_work["Size"] = df_client["Size"].map(lambda x: strip_string(x)) ###
        df_sanveo_work["Size"] = df_sanveo_work["Size"].map(lambda x: strip_string(x))  ###


    if "Length" in selected_cols:
        df_client_work["Length"] = df_client_work["Length"].map(lambda x: char_2_dig(x))
        df_sanveo_work["Length"] = df_sanveo_work["Length"].map(lambda x: char_2_dig(x))



    df_client_work = df_client_work.applymap(lambda x: str(x).lower())
    df_sanveo_work = df_sanveo_work.applymap(lambda x: str(x).lower())
    client_feat = list(df_client_work.agg(" ".join, axis=1))
    cat_feat = list(df_sanveo_work.agg(" ".join, axis=1))  ## sanveo catalogue feature
    cat_lab = list(df_sanveo["ID"].values) ## sanveo catalogue labels

    cat_feat_ind_dict = dict((key, val) for val, key in enumerate(cat_feat))

    feat_2_label_dict = {}
    label_2_feat_dict = {}

    for i, f in enumerate(cat_feat):
        feat_2_label_dict[f] = cat_lab[i]
        label_2_feat_dict[cat_lab[i]] = f

    ## Referece dictionary building for multiple predicitons
    ref_dict_for_multiple_preds = {}
    for i, f in enumerate(cat_feat):
        
        if f not in ref_dict_for_multiple_preds:
            ref_dict_for_multiple_preds[f] =[ cat_lab[i] ]
        else:     
            ref_dict_for_multiple_preds[f].append(cat_lab[i])
       


    result = []
    conf_list = []
    label_list_multiple = []
    conf_list_multiple = []

    count = 0

    for ind, sample in enumerate(client_feat):

        ## logic for one, three and five best
        # sample_number = "sample_number_" + str(ind + 1)
        findings = process.extract(sample, cat_feat, scorer=fuzz.ratio, limit=1)
        pred_labels, pred_confs, features = find_labels(cat_feat_ind_dict, cat_lab, findings)
        label = pred_labels[0]
        conf = pred_confs[0]
        conf_list.append(conf)
        if conf == 100:
            result.append(label)
        elif conf > 85 and conf < 100:
            findings = process.extract(sample, cat_feat, scorer=fuzz.ratio, limit=3)
            pred_labels, _, _ = find_labels(cat_feat_ind_dict, cat_lab, findings)
            result.append(pred_labels)
        else:
            findings = process.extract(sample, cat_feat, scorer=fuzz.ratio, limit=5)
            pred_labels, _, _ = find_labels(cat_feat_ind_dict, cat_lab, findings)
            result.append(pred_labels)


        ## For multiple predictions
        # try: 
        #     findings = process.extract(sample, cat_feat, scorer=fuzz.ratio, limit=len(cat_feat))
        #     res = find_multiple_labels(findings, ref_dict_for_multiple_preds)
        #     count += 1
    
        #     conf = list(res['confidence'].keys())[0]
        #     print(f"Printing the confidence value")
        #     print(conf)

        #     print('***********before labels*************')
            
        #     labels = res['confidence'][conf]

        #     print('***********after labels**************')

        #     if conf != '100':
        #         if len(labels) > 20: ## We don't want more than 20 labels for confidence below 100, when it is for multiple prediction
        #             label_list_multiple.append(labels[0:20])
        #             conf_list_multiple.append(conf)
        #             continue

        #     label_list_multiple.append(labels)
        #     conf_list_multiple.append(conf)
        # except Exception as error:
        #     print(f"The error is {error}")
        #     print('***********Danger Danger Danger****************************************************************Danger Danger')
        #     label_list_multiple.append("NA")
        #     conf_list_multiple.append("NA")


        
        findings = process.extract(sample, cat_feat, scorer=fuzz.ratio, limit=len(cat_feat))
        res = find_multiple_labels(findings, ref_dict_for_multiple_preds)
        count += 1

        conf = list(res['confidence'].keys())[0]
        print(f"Printing the confidence value")
        print(conf)

        print('***********before labels*************')
        
        labels = res['confidence'][conf]

        print('***********after labels**************')

        if conf != '100':
            if len(labels) > 20: ## We don't want more than 20 labels for confidence below 100, when it is for multiple prediction
                label_list_multiple.append(labels[0:20])
                conf_list_multiple.append(conf)
                continue

        label_list_multiple.append(labels)
        conf_list_multiple.append(conf)
        print('************************length of confidence*********************')
        print(len(conf_list_multiple))
        print(len(label_list_multiple))





    df_client_work_multiple = copy.deepcopy(df_client_work)
    df_client_work_multiple["Predicted_multiple_labels"] = label_list_multiple
    df_client_work_multiple["Confidence"] = conf_list_multiple

    df_client_work["Predicted_label"] = result
    df_client_work["Confidence"] = conf_list



    output_filename = client_filename.split('.')[0] + "_" + "output.csv"
    output_filename_multiple = client_filename.split('.')[0] + "_" + "output_multiple.csv"

    if os.path.exists(os.path.join(OUTPUT_FOLDER, output_filename)):
        os.remove(os.path.join(OUTPUT_FOLDER, output_filename))

    if os.path.exists(os.path.join(OUTPUT_FOLDER, output_filename_multiple)):
        os.remove(os.path.join(OUTPUT_FOLDER, output_filename_multiple))


    df_client_work.to_csv(os.path.join(OUTPUT_FOLDER, output_filename))
    df_client_work_multiple.to_csv(os.path.join(OUTPUT_FOLDER, output_filename_multiple))

    msg = "Processing Finished"
    down_msg = "Download the output file"
    down_msg_multiple = "Download the multiple predictions output file"

    resp['message_match'] = check_msg
    resp['message_finish'] = msg
    resp['flag'] = 1
    resp['download_msg'] = down_msg
    resp['download_msg_multiple'] = down_msg_multiple


    #return resp
    return HttpResponse(json.dumps(resp), content_type="application/json")

def download(request):
    global output_filename
    path = os.path.join(OUTPUT_FOLDER, output_filename)


    if os.path.exists(path):
        with open(path, 'r') as fl:
            fl = open(path, 'r')

            mime_type, _ = mimetypes.guess_type(path)
            resp = HttpResponse(fl, content_type=mime_type)
            resp['Content-Disposition'] = "attachment; filename=%s" % output_filename

        return resp
    raise Http404

def download_multiple(request):
    global output_filename_multiple
    path = os.path.join(OUTPUT_FOLDER, output_filename_multiple)

    if os.path.exists(path):
        with open(path, 'r') as fl:
            mime_type, _ = mimetypes.guess_type(path)
            resp = HttpResponse(fl, content_type=mime_type)
            resp['Content-Disposition'] = "attachment; filename=%s" % output_filename_multiple

        return resp
    raise Http404