# CS50 WEB FINAL PROJECT: LEARN ENGLISH WORD

Project video: https://youtu.be/X-KcN-rJAYA

## Overview

The project is a web application for learning English vocabularies. Everyone can get the meaning of words, collect favorite words and take test from
users' favorite words. The main comonents are as following.
* Home page
* Login/Logout/Register
* Search page that provides definitions, audios and images of words.
* Test page can help user familiar with collected vocabularies.
*	Favorite page display users' favorite words.
*	Upload page in whcih user can upload excel file to extend their collected words.

## Distinctiveness and Complexity
As a non-native English speaker, I struggle in the way of learning English words. So I create a customized web application to learn English vocabularies. The web application is not a social media app nor an e-commerce app.

The web application utilizes Djangoon for the backend and Javascript for the front end. It is mobile-responsive as well.
The appliction extracts data like definition, audios and images from other three websites. When exctracting or loading data, the page displays loading spinner. The application can generate test questions from users' favorite words.
Also, the user can upload .xlsx file to the web application for extending favorite words and show content of sheet1 of the file.

## Run Application
#### On Windows:
* Clone the repository

* Create a virtual environment and activate it
```
pip3 install virtualenv
cd \path\to\new\virtual\environment
virtualenv env(folder name you like)
env\Scripts\activate.bat
```

* Install the dependencies using
```
cd \path\to\root directory
pip3 install -r requirements.txt
```

* Start the server
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Files Information
### Front End
* ./static/images/
  * header.jpg - background image for home page
  * sub_header.jpg - background image for search/test/upload/favorite page
* ./static/memorize/
  * features.js - javascript used for all pages except login/register page
  * styles.css - css used for all pages except login/register page	
* ./templates/memorize/
  * base.html - base template and for home page
  * index.html - template for search/test/upload/favorite page

### Back End
* ./models.py
  * There are 4 models for the web application's database.
    * User - Custom User model extending AbstractUser.
    * Word - Holds the information of words.
    * Phrase - Holds the information of the example sentences.
    * FavouriteList - Collected words of users.

* ./bing/
  * bing.py - Python library to download bulk of images form bing.com
  * Reference: https://github.com/gurugaurav/bing_image_downloader (is licensed under MIT License)
* ./forvo/
  * Get definition, example sentence and pronunciation.
    * dictobject.py - Interface for providing API to views.py
    * dictionary.py - Implementation for getting definition from https://en.wiktionary.org/
    * forvo.py - Implementation for getting audios from forvo.com
    * Reference: https://github.com/FreeLanguageTools/vocabsieve (is licensed under GNU General Public License v3.0)

* ./views.py
  * The main functions are as following.
    * get_word_info(request, word) 
	    * If word does not exist in local database, get information from external
	  websites and store to database. Else, get information from database.	
    * user_list(request)
	    * Get all names of registered users.
    * favor_list(request, username)
	    * CRUD model FavouriteList of request user. 
    * handle_upload(request)
	    * Handle uploaded excel file. If the word is not in database, store it to model FavouriteList of request user.
	    * Reference: https://github.com/anuragrana/excel-file-upload-django

## File Structure
```
|   manage.py
|   requirements.txt
|   
+---memorize
|   |   admin.py
|   |   apps.py
|   |   models.py
|   |   tests.py
|   |   urls.py
|   |   views.py
|   |   __init__.py
|   |   
|   +---bing
|   |       bing.py
|   |       
|   +---forvo
|   |       constants.py
|   |       dictformats.py
|   |       dictionary.py
|   |       dictobject.py
|   |       forvo.py
|   |       lemmatizer.py
|   |       playsound.py
|   |       tools.py
|   |       
|   +---static
|   |   +---images
|   |   |       header.jpg
|   |   |       sub_header.jpg
|   |   |       
|   |   \---memorize
|   |           features.js
|   |           styles.css
|   |           
|   \---templates
|       \---memorize
|               index.html
|               base.html
|               login.html
|               register.html
|               
\---project_final
        asgi.py
        settings.py
        urls.py
        wsgi.py
        __init__.py
```
