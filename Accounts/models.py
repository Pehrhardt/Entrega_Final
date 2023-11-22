from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.conf import settings

# Clase para guardar el Avatar
class Avatar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='avatares', null=True, blank = True)
 
    def __str__(self):
        return f"{self.user} - {self.imagen}"

# Creamos la clase Post con título, un nombre en la url por cada post(slug), fecha de creacion, el autor que serán los usuarios y
# las categorias que un post puede tener muchas categorías y si el post es destacado o no
class Post (models.Model):
    titulo=models.CharField(max_length=200)
    slug=models.SlugField(unique=True)
    resumen= models.CharField (max_length=300 , default='sin resumen')
    fecha= models.DateTimeField(auto_now_add=True)
    contenido=models.TextField (max_length=10000, default='sin contenido')
    autor=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    categoria=models.ManyToManyField('categorias',default="Sin categoria")
    destacado= models.BooleanField(default=False)
    imagen=models.ImageField(upload_to='Blog_image', null=True , blank=True)
    now_date=models.DateTimeField(default=timezone.now)

    class meta:
        ordering= ["-fecha"] # Para que muestre los ultimos blogs creados primeros

    def __str__ (self): 
        return self.titulo


    
# Creamos el modelo categoria

class Categorias (models.Model):
    titulo=models.CharField(max_length=200)
    slug=models.SlugField(unique=True)

    class meta:
        verbose_name_plural= 'categorias'

    def __str__ (self): 
        return self.titulo






