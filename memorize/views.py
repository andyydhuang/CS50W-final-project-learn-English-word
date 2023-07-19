import json
import re
import openpyxl

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *
from .forvo.dictobject import DictObject
from .bing.bing import Bing
import time
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from inspect import signature

IMAGE_SEARCH_KEYWORD = ' images related to definition '

def index(request):
    return render(request, "memorize/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "memorize/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "memorize/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def upload_view(request):
    return render(request, "memorize/upload.html")

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "memorize/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "memorize/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "memorize/register.html")


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

def get_word_info(request, word):
    use_lemmatize = None
    if request:
        use_lemmatize = str2bool(request.GET.get("lemmatize", "True"))

    item = DictObject().lookup(word, use_lemmatize)
    word = item['word']
    word = word.lower()
    item['word'] = word

    qs = Word.objects.filter(name = word)
    if qs.exists() == False:
        data_dict = { "audios" : DictObject().lookupAudio(word) }
        data_dict.update(item)

        if 'Definition for' in data_dict['definition'] and 'not found' in data_dict['definition']:
            if request:
                return JsonResponse({'name': data_dict['word'] , 'defn':data_dict['definition']})
            else:
                return None
        else:
            word_obj = store_word_and_phrases(data_dict)
            #Fetch MIMG links
            bing = Bing(
                query=IMAGE_SEARCH_KEYWORD+word,
                limit=2,
                output_dir="dataset",
                adult=True,
                timeout=60,
                filter="",
                verbose=True,
            )
            mimg_list = bing.get_image_link()
            if len(mimg_list) > 0:            
                word_obj.set_mimgs(mimg_list)
                word_obj.save()

    if request:
        word_obj = Word.objects.get(name = word)
        dict1 = word_obj.serialize()
        dict2 = {'phrases' : []}
        for phrase_obj in word_obj.phrases.all():
            dict2['phrases'].append(phrase_obj.serialize())
        dict2.update(dict1)
        dict2.update({'is_in_favor': is_in_favor(request, word)})
        cached_mimgs = word_obj.get_mimgs()
        dict2.update({'mimgs': word_obj.get_mimgs()})
        return JsonResponse(dict2)
    return word

'''
def search(word):
    use_lemmatize = True
    item = DictObject().lookup(word, use_lemmatize)
    word = item['word']
    word = word.lower()
    item['word'] = word

    qs = Word.objects.filter(name = word)
    if qs.exists() == False:
        data_dict = { "audios" : DictObject().lookupAudio(word) }
        data_dict.update(item)

        if 'Definition for' in data_dict['definition'] and 'not found' in data_dict['definition']:
            return None
        else:
            word_obj = store_word_and_phrases(data_dict)
            bing = Bing(
                query=word+IMAGE_SEARCH_KEYWORD_POSTFIX,
                limit=2,
                output_dir="dataset",
                adult=True,
                timeout=60,
                filter="",
                verbose=True,
            )
            mimg_list = bing.get_image_link()
            if len(mimg_list) > 0:            
                word_obj.set_mimgs(mimg_list)
                word_obj.save()
    return word
'''

def store_word_and_phrases(input):
    word = input['word']

    audio_link = None
    try:
        audio_link = input['audios'][word]
    except:
        try:
            word = word[0].upper() + word[1:]
            audio_link = input['audios'][word]
        except:
            pass

    try:
        word_obj = Word.objects.create(name=input['word'] , defn=input['definition'],
            audio_link=audio_link)
        input['audios'].pop(word, None)
        for k, v in input['audios'].items():
            #print(f"k:{k} v:{v}")
            phrase_obj = Phrase.objects.create(name=k, audio_link=v, word=word_obj)
        #Word.objects.create(name=input['word'] , defn=input['definition'], audio_link=None)
        return word_obj
    except:
        return None

def is_in_favor(request, word):
    favourite_list_obj = None

    try:
        favourite_list_obj = FavouriteList.objects.get(username=request.user.username)
    except FavouriteList.DoesNotExist:
        favourite_list_obj = FavouriteList.objects.create(username = request.user.username)

    return favourite_list_obj.words.filter(name=word).exists()

@csrf_exempt
@login_required
def favor_list(request, username):
    try:
        favor_list = FavouriteList.objects.get(username = username)
    except FavouriteList.DoesNotExist:
        return JsonResponse({"error": "FavouriteList not found."}, status=404)

    # Return profile contents
    if request.method == "GET":
        favor_word_list = []
        words = favor_list.words.all()
        for word in words:
          #print(f"word:{word}")
          favor_word_list.append(word.name)

        res_dict = {
            "favor_word_list": favor_word_list,
        }
        #print(f"res_dict:{res_dict}")
        return JsonResponse(res_dict, status=200)

    # Update follow or unfollow
    elif request.method == "PUT":
        data = json.loads(request.body)  

        use_lemmatize = True
        item = DictObject().lookup(data["word"], use_lemmatize)
        word = item['word']	
        word = word.lower()
        item['word'] = word
        
        #word_obj = Word.objects.get(name = data["word"])
        word_obj = Word.objects.get(name = word)

        if data.get("favor_action") is not None:
            favor_action = data["favor_action"]
            if (favor_action == 'true'):
                #poster.users.add(request.user)

                favor_list.words.add(word_obj)
            elif (favor_action == 'false'):
                #poster.users.remove(request.user)
                favor_list.words.remove(word_obj)
        return HttpResponse(status=204)
    # Profile must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


@login_required
def word_in_favor_list(request, username, word):

    use_lemmatize = True
    item = DictObject().lookup(word, use_lemmatize)
    word = item['word']
    word = word.lower()
    item['word'] = word

    if request.method == "GET":
        try:
            favor_list = FavouriteList.objects.get(username = username)
        except FavouriteList.DoesNotExist:
            return JsonResponse({"error": "FavouriteList not found."}, status=404)

        is_in_favor = favor_list.words.filter(name=word).exists()
        res_dict = {
            "is_in_favor": is_in_favor,
        }
        return JsonResponse(res_dict)
    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)

@login_required
def user_list(request):
    if request.method == "GET":
        user_names = User.objects.all().values('username')
        all_names = [u['username'] for u in user_names]

        res_dict = {
            "all_names": all_names,
        }
        return JsonResponse(res_dict)
    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)        

'''
@csrf_exempt
@login_required
def upload_favor(request):
    if request.method == "POST":
        encoding = 'utf-8'
        str_data = str(request.body, encoding)

        m = re.search('plain(.+?)------WebKitForm', str_data)
        if m:
            found = m.group(1)
            print(f"found:[{found}]")

        return HttpResponse(status=204)
    else:
        return JsonResponse({
            "error": "POST request required."
        }, status=400)
'''

@login_required
def handle_upload(request):
    if "POST" == request.method:
        excel_file = request.FILES["excel_file"]

        # you may put validations here to check extension or file size

        wb = openpyxl.load_workbook(excel_file)

        # getting a particular sheet by name out of many sheets
        worksheet = wb["Sheet1"]
        #print(worksheet)

        excel_data = list()
        # iterating over the rows and
        # getting value from each cell in row
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            excel_data.append(row_data)

        # Create Mode FavouriteList if not exist
        favourite_list_obj = None
        try:
            favourite_list_obj = FavouriteList.objects.get(username=request.user.username)
        except FavouriteList.DoesNotExist:
            favourite_list_obj = FavouriteList.objects.create(username = request.user.username)

        for item in excel_data:
            for ele in item:
                if ele.isalpha():
                    found_word = get_word_info(None, ele)
                    #print(f"found_word:{found_word}") 

                    if found_word and favourite_list_obj.words.filter(name=found_word).exists() == False:
                    #!= None and favourite_list_obj.words.filter(name=found_word).exists() == False:
                        word_obj = Word.objects.get(name=found_word)
                        favourite_list_obj.words.add(word_obj)

        return render(request, 'memorize/index.html', {"excel_data":excel_data, "type":"upload"})
    else:
        return JsonResponse({
            "error": "POST request required."
        }, status=400)




