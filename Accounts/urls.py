
from django.contrib import admin
from django.urls import path
from .views import Index,Login,Registro,salir,editarperfil,verperfil,cargaravatar,about,Posts,PostDetailView,Lista_de_categorias,BuscadorResultado, publicar_posts,MisPosts,EliminarPost,editar_post,ListaCategorias,EliminarCat,EditarCategoria,CrearCategoria
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #Paginas 
    path('', Index.as_view(), name='index'),
    path('about/',about.as_view(),name='about'),
    # Login y registro 
    path('login/', Login.as_view(), name='login'),
    path('register/', Registro.as_view(), name='register'),
    path('index/', salir, name='salir'),
    path('editarperfil/', editarperfil.as_view(), name='editarperfil'),
    path ('perfil/', verperfil.as_view(), name="verperfil"),
    path ('cargaavatar/',cargaravatar, name="Avatar"),
    
    # Mostrar Posts y busquedas 
    path ('Blogs/', Posts, name='Blogs'),
    path ('Post/<slug:slug>', PostDetailView.as_view(), name="Post"),
    path ('categorias/<slug:slug>',Lista_de_categorias.as_view(), name="RCategoria"),
    path ('results/',BuscadorResultado.as_view(), name="buscar"),
    path ('Misposts/',MisPosts.as_view(), name="mispost"),

    # Funciones del Blog
    path ('publicar/',publicar_posts.as_view(), name="publicar"),
    path('eliminar/<slug:post_slug>/', EliminarPost.as_view(), name='eliminar_post'),
    path ('EditarPost/<int:post_id>//',editar_post.as_view(), name="editar_post" ),

    #Funciones Categorias
     path('ListaCategorias/', ListaCategorias.as_view(), name='lista_categorias'),
     path ('eliminarc/<slug:categoria_slug>/', EliminarCat.as_view(), name="eliminar_cat"),
    path('editar_categoria/<int:categoria_id>/', EditarCategoria.as_view(), name='editar_categoria'),
    path('crear-categoria/', CrearCategoria.as_view(), name='crear_categoria'),






]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

