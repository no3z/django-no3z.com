from django.db import models
from no3z_www.filebrowser.fields import FileBrowseField

# Create your models here.
class Noticia(models.Model):
    title = models.CharField(max_length=140, unique=True)
    description = models.CharField(max_length=512)
    link = models.URLField(verify_exists=False)
    image =   FileBrowseField("Image (Format)", max_length=200, format='Image', blank=True)
    author = models.CharField(max_length=150)
    music = FileBrowseField("mp3", max_length=200, format='Audio', blank=True, null=True)
    pubDate = models.DateField( null=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
    	return self.title