from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from app.models import Photo,Category,Year,Video,Contact
import json


def index(request):
    years=Year.show_all_years()
    photos = Photo.show_recent_photos()
    videos = Video.show_recent_videos()
    return render(request, "gallery/index.html", context={"photos":photos,"videos":videos,"years":years})



def get_category(request):
    id = request.GET.get('id', '')
    result = list(Category.objects.filter(
    year_id=int(id)).values('id', 'name'))
    return HttpResponse(json.dumps(result), content_type="application/json")


def browse(request):
    term=request.GET.get("s")
    categories = Category.search_category_by_id(term)
    years=Year.show_all_years()
    videos = Video.search_video_by_category(term)
    photos = Photo.search_photo_by_category(term)
    return render(request, "gallery/browse.html", context={"photos":photos,"videos":videos,"categories":categories,"years":years})

def browsecategories(request):
    term=request.GET.get("s")
    years=Year.show_all_years()
    categories = Category.search_category_by_year(term)
    return render(request, "gallery/browsecategories.html", context={"categories":categories,"term":term,"years":years})

def search(request):
    term=request.GET.get("search")
    years=Year.show_all_years()
    photos = Photo.search_photo(term)
    videos = Video.search_video(term)
    categories=Category.search_category(term)
    return render(request, "gallery/search.html", context={"photos":photos,"videos":videos,"categories":categories,"search":term,"years":years})

def about(request):
    years=Year.show_all_years()
    return render(request, "gallery/about.html", context={"years":years})

def contacts(request):
    years=Year.show_all_years()
    contacts=Contact.show_all_contacts()
    return render(request, "gallery/contacts.html", context={"years":years,"contacts":contacts})
