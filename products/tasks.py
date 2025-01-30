from celery import shared_task
from easy_thumbnails.files import get_thumbnailer

@shared_task
def create_thumbnail(image_path):
    thumbnail_options = {'size': (100, 100), 'crop': True}
    thumbnailer = get_thumbnailer(image_path)
    thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
    return thumbnail.url