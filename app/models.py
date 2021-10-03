from django.db import models
import pyperclip
import random
from django.db.models import Q
from .validators import validate_file_extension
from django.core.validators import FileExtensionValidator
import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django import forms
from sorl.thumbnail import get_thumbnail
from django.utils.html import format_html
import pyfiglet
import wget
import urllib,json
from urllib import request
import requests
import os
from django.core.files import File

class Year(models.Model):
    year = models.CharField(max_length=4,unique=True)

    def __str__(self):
        return self.year

    def save_year(self):
        return self.save()

    @classmethod
    def show_all_years(cls):
        return cls.objects.order_by("year")[::-1]

    @classmethod
    def search_year(cls, search):
        qset=cls.objects.filter(year__icontains = search)
        return qset.order_by("year")


class Category(models.Model):
    name = models.CharField(max_length=144)
    year = models.ForeignKey(Year,on_delete=models.CASCADE,default=1)

    class Meta:
       unique_together = ('name', 'year',)

    def __str__(self):
        return self.name

    def save_category(self):
        return self.save()

    @classmethod
    def show_all_categories(cls):
        return cls.objects.order_by("name")[::-1]
        
    @classmethod
    def search_category_by_year(cls, search):
        return cls.objects.filter(year__year__exact = search).order_by("name")
        
    @classmethod
    def search_category_by_id(cls, search):
        a=cls.objects.filter(id__exact = search).order_by("name")
        return a

    @classmethod
    def search_category(cls, search):
        qset=cls.objects.filter(name__icontains = search )
        return qset.order_by("name")


class Photo(models.Model):
    name = models.CharField(max_length=244)
    year=models.ForeignKey(Year,on_delete=models.CASCADE,default=1,null=False,blank=False)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,default=None)
    post_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to ='images/')
    thumbnail = models.ImageField(upload_to='thumbs/', editable=False)

    @property
    def thumbnail_preview(self):
        if self.image:
            _thumbnail = get_thumbnail(self.image,
                                   '200x200',
                                   upscale=False,
                                   crop=False,
                                   quality=70)
            return format_html('<img src="{}" width="{}" height="{}">'.format(_thumbnail.url, _thumbnail.width, _thumbnail.height))
        return ""


    def save(self, *args, **kwargs):
        if not self.id:
            self.image = self.compressImage(self.image)
            self.thumbnail= self.thumbImage(self.image)
        super(Photo, self).save(*args, **kwargs)

    def compressImage(self,image):
        imageTemproary = Image.open(image)
        outputIoStream = BytesIO()
        if imageTemproary.size[1] > 1000 or imageTemproary.size[0] > 1000:
             fixed_height = 1000
             height_percent = (fixed_height / float(imageTemproary.size[1]))
             width_size = int((float(imageTemproary.size[0]) * float(height_percent)))
             imageTemproary = imageTemproary.resize((width_size, fixed_height))
        imageTemproary.save(outputIoStream , format='JPEG',optimize=True, quality=70)
        outputIoStream.seek(0)
        image = InMemoryUploadedFile(outputIoStream,'ImageField', "%s.jpg" % image.name.split('.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
        return image
    
    def thumbImage(self,image):
        imageTemproary = Image.open(image)
        outputIoStream = BytesIO()
        if imageTemproary.size[1] > 300 or imageTemproary.size[0] > 300:
             fixed_height = 300
             height_percent = (fixed_height / float(imageTemproary.size[1]))
             width_size = int((float(imageTemproary.size[0]) * float(height_percent)))
             imageTemproary = imageTemproary.resize((width_size, fixed_height))
        imageTemproary.save(outputIoStream , format='JPEG',optimize=True, quality=70)
        outputIoStream.seek(0)
        image = InMemoryUploadedFile(outputIoStream,'ImageField', "%s.jpg" % image.name.split('.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
        return image

    def __str__(self):
        return self.name

    def save_photo(self):
        return self.save()

    @classmethod
    def copy_url(cls, id):
        photo = cls.objects.get(id = id)
        pyperclip.copy(photo.image.url)
  
    @classmethod
    def show_recent_photos(cls):
        return cls.objects.order_by("post_date")[::-1][:10]

    @classmethod
    def show_all_photos(cls):
        return cls.objects.order_by("post_date")[::-1]

    @classmethod
    def show_random_photo(cls):
        all_photos = cls.show_all_photos()
        random_id = random.randint(1, len(all_photos))
        return cls.objects.get(id = random_id)

    @classmethod
    def delete_photo(cls, id):
        return cls.objects.filter(id__exact = id).delete()

    @classmethod
    def get_photo_by_id(cls, id):
        return cls.objects.filter(id__exact = id)[0]

    @classmethod
    def search_photo_by_year(cls, search):
        return cls.objects.filter(year__year__exact = search).order_by("post_date")[::-1]

    @classmethod
    def search_photo_by_category(cls, search):
        return cls.objects.filter(category__id__exact = search).order_by("post_date")[::-1]

    @classmethod
    def search_photo(cls, search):
        qset=cls.objects.filter(Q(name__icontains = search)  )
        return qset.order_by("post_date")[::-1]



class Video(models.Model):
    name = models.CharField(max_length=244,editable=False)
    year=models.ForeignKey(Year,on_delete=models.CASCADE,default=1,null=False,blank=False)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,default=None)
    post_date = models.DateTimeField(auto_now_add=True)
    youtube_video_url=models.CharField(max_length=244)
    videothumbs = models.ImageField(upload_to='vidthumbs/', editable=False)

    def save(self, *args, **kwargs):
        if self.youtube_video_url and not self.videothumbs:

            url = self.thumbVideo(self.youtube_video_url)
            result = request.urlretrieve(url)
            self.videothumbs.save(
                os.path.basename(self.youtube_video_url)+".jpg",
                File(open(result[0], 'rb'))
                )
            self.name = self.nameVideo(self.youtube_video_url)            
        super(Video, self).save(*args, **kwargs)

    def thumbVideo(self,youtube_video_url):
        url=self.youtube_video_url
        id=url.split("=",1)[1]
        thumb = 'https://i.ytimg.com/vi/'+id+'/hqdefault.jpg'
        return thumb
    
    def nameVideo(self,youtube_video_url):
        url=self.youtube_video_url
        id=url.split("=",1)[1]
        names = 'https://www.youtube.com/oembed?url=http%3A//youtube.com/watch%3Fv%3D'+id+'&format=json'
        response = urllib.request.urlopen(names)
        data = json.loads(response.read())
        return data['title']


    def __str__(self):
        return self.name

    def save_video(self):
        return self.save()


    @classmethod
    def show_recent_videos(cls):
        return cls.objects.order_by("post_date")[::-1][:10]

    @classmethod
    def show_all_videos(cls):
        return cls.objects.order_by("post_date")[::-1]

    @classmethod
    def show_random_video(cls):
        all_photos = cls.show_all_videos()
        random_id = random.randint(1, len(all_photos))
        return cls.objects.get(id__exact = random_id)

    @classmethod
    def delete_video(cls, id):
        return cls.objects.filter(id__exact = id).delete()

    @classmethod
    def get_video_by_id(cls, id):
        return cls.objects.filter(id__exact = id)[0]

    @classmethod
    def search_video_by_year(cls, search):
        return cls.objects.filter(year__year__exact = search).order_by("post_date")[::-1]

    @classmethod
    def search_video_by_category(cls, search):
        return cls.objects.filter(category__id__exact = search).order_by("post_date")[::-1]

    @classmethod
    def search_video(cls, search):
        qset=cls.objects.filter(Q(name__icontains = search)  )
        return qset.order_by("post_date")[::-1]

class Contact(models.Model):
    name = models.CharField(max_length=244)
    email_id=models.CharField(max_length=244,blank=True,null=True)
    contact_number=models.CharField(max_length=244,blank=True,null=True)
    
    def __str__(self):
        return self.name

    def save_contact(self):
        return self.save()
    
    @classmethod
    def show_all_contacts(cls):
        return cls.objects.order_by("name")
