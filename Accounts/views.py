from django.shortcuts import render, redirect
from django.contrib.auth import login,logout    
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView, CreateView
from django.db.models import Max
from django.urls import reverse_lazy
from django.views import generic,View
from .forms import RegistroUsuario, UserEdit , AvatarForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Avatar,Post,Categorias
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.text import slugify
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
import os

# Creo las vistas del Login y el redireccionamiento en caso de que el Login sea exitoso al index.
class Index (LoginRequiredMixin,TemplateView):
    template_name = 'Accounts/index.html'

class verperfil (LoginRequiredMixin,TemplateView):
    template_name = 'Accounts/verperfil.html'

class about(LoginRequiredMixin,TemplateView):
    template_name = 'Accounts/about.html'

class Login(LoginView):
    template_name = 'Accounts/login.html'
    redirect_authenticated_user = True  # Esto redirige a los usuarios autenticados
 # Esta función, si el usuario está autenticado, redirige a la página de inicio
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

# Creo la carga de formulario, si es valido guarda el usuario con los correspondientes datos
class Registro(FormView):
    template_name = 'Accounts/register.html'
    form_class = RegistroUsuario
    redirect_autheticated_user = True
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.save()
        user=form.save()
        if user is not None:
            login(self.request, user)
        return super(Registro, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
         return redirect('index')
        return super(Registro,self).get(*args, **kwargs)

# Log Out
def salir(request):
    logout(request)
    return redirect('index')

    # Editar Perfil:
class editarperfil(LoginRequiredMixin, FormView):
    template_name = 'Accounts/editarperfil.html'
    form_class = UserEdit
    success_url = reverse_lazy('verperfil')

    def form_valid(self, form):
        usuario = self.request.user
        informacion = form.cleaned_data
        usuario.email = informacion['email']
        usuario.set_password(informacion['password1'])
        usuario.last_name = informacion['last_name']
        usuario.first_name = informacion['first_name']
        usuario.save()

        return redirect ('verperfil')

    def get_initial(self):
        usuario = self.request.user
        return {'email': usuario.email, 'last_name': usuario.last_name, 'first_name': usuario.first_name}
    
# Formulario para cargar el Avatar, si el usuario ya posee uno se puede cambiar y se reemplaza.

@login_required
def cargaravatar(request):
    usuario = request.user
    if request.method == 'POST':
        miFormulario = AvatarForm(request.POST, request.FILES)
        if miFormulario.is_valid():
            avatares = Avatar.objects.filter(user=usuario)
            if avatares.exists():
                # Si existen avatares asociados al usuario, actualiza el primero encontrado
                avatar = avatares.first()
                avatar.imagen = miFormulario.cleaned_data['imagen']
                avatar.save()
            else:
                # Si no hay avatares, crea uno nuevo
                avatar = Avatar(user=usuario, imagen=miFormulario.cleaned_data['imagen'])
                avatar.save()

            # Redirigir a la página donde muestra el perfil
            return render(request, "Accounts/verperfil.html")  

    else:
        miFormulario = AvatarForm()
    
    return render(request, "Accounts/cargaavatar.html", {"miFormulario": miFormulario})


# Muestra los posts creados en la página Blog y muestra en el carrousel los primeros 3 destacados
@login_required
def Posts (request):
    posts= Post.objects.all().order_by('-fecha')
    lista_categorias=Categorias.objects.all()
    destacados=Post.objects.filter(destacado=True)[:3]
    context= { 
        'lista_post' :posts,
        'lista_categorias' : lista_categorias,
        'destacados' : destacados,
    }
    return render (request,"Accounts/blogs.html", context=context)

# Muestra en detalle el Post en una pagina
class PostDetailView (LoginRequiredMixin,generic.DetailView):
     model=Post
     template_name= 'Accounts/post_detalle.html'
    
    # Llamo las listas de categorías y Posts a todos los articulos
     def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['lista_categorias'] = Categorias.objects.all()
        context['lista_post'] = Post.objects.all().order_by('-fecha')
        return context
     

# Función para que se pueda enviar el nombre del titulo de categoria al buscador categorias.html
def obtener_titulo_categoria(path):
    query = path.replace('/categorias/', '')
    categoria = get_object_or_404(Categorias, slug=query)
    return categoria.titulo if categoria else None
     
# Clase creada para retornar los blogs por categoria 
class Lista_de_categorias(LoginRequiredMixin,generic.ListView):
    model= Post
    template_name= 'Accounts/categorias.html'

    def get_queryset(self):
        query = self.request.path.replace('/categorias/', '')
        print(query)
        post_list = Post.objects.filter(categoria__slug=query).filter(
            now_date__lte=timezone.now()).order_by('-fecha') 
        return post_list
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lista_categorias'] = Categorias.objects.all()
        context['categoria_titulo'] = obtener_titulo_categoria(self.request.path)
        return context
    
# Con esta función se buscara por titulo o por categoria en el buscador de index
class BuscadorResultado(LoginRequiredMixin, generic.ListView):
    model = Post
    template_name = 'Accounts/results.html'

    def get_queryset(self):
        query = self.request.GET.get('search')
         # Que contenga lo que busco  dentro del titulo o letras de las categorias
        post_list = Post.objects.filter(
            Q(titulo__icontains=query) | Q(categoria__titulo__icontains=query)
        ).filter(
            now_date__lte=timezone.now()
        ).distinct().order_by('-fecha')
        return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('search')
        context['categoria_titulo'] = Categorias.objects.all()
        context['query']= query
        return context
    
# Crear un nuevo Post

class publicar_posts(LoginRequiredMixin,View):
    template_name = 'Accounts/Publicar.html'
    success_url = reverse_lazy('Blogs')

    def get(self, request, *args, **kwargs):
        lista_categorias = Categorias.objects.all()
        return render(request, self.template_name, {'lista_categorias': lista_categorias})

    def post(self, request, *args, **kwargs):
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        resumen = request.POST.get('resumen')
        categoria_id = request.POST.get('categoria')
        imagen = request.FILES.get('imagen')

        categoria = Categorias.objects.get(id=categoria_id)
        autor = self.request.user

        slug = slugify(titulo)

         # Verificar la unicidad del slug y hacerlo único si es necesario
        slug_original = slug
        i = 1
        while Post.objects.filter(slug=slug).exists():
            slug = f'{slug_original}-{i}'
            i += 1
        # Crear y guardar el nuevo post
        post = Post.objects.create(
            titulo=titulo,
            contenido=contenido,
            resumen=resumen,
            imagen=imagen,
            autor=autor,
            slug=slug
        )
        # Asignar la categoría al post usando el método set()
        post.categoria.set([categoria])

        return HttpResponseRedirect(self.success_url)
    

# Mostrar los Post de un determinado Usuario
class MisPosts(LoginRequiredMixin, generic.ListView):
    model = Post
    template_name = 'Accounts/Misposts.html'
    context_object_name = 'lista_post' 

    def get_queryset(self):
        # Filtrar los posts por el autor que sea el usuario autenticado actualmente
        return Post.objects.filter(autor=self.request.user).order_by('-fecha')

# Clase con función para eliminar los Post si el usuario es el autor.
class EliminarPost(View):
    def get(self, request, post_slug):
        post = get_object_or_404(Post, slug=post_slug)

        # Verificar si el usuario tiene permiso para eliminar el post
        if request.user != post.autor:
            return redirect('mispost') 

        # Si el usuario tiene permiso, elimina el post
        post.delete()
        return redirect('mispost')
    
# Editar Post

class editar_post (LoginRequiredMixin,View):

    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        lista_categorias = Categorias.objects.all()
        context = {
            'post': post,
            'lista_categorias': lista_categorias
        }
        return render(request, 'Accounts/EditarPost.html', context)
            
    def post(self, request, post_id):     
        post = Post.objects.get(id=post_id)
        # Actualizar el post con los datos del formulario
        post.titulo = request.POST.get('titulo')
        post.contenido = request.POST.get('contenido')
        post.resumen = request.POST.get('resumen')
        # Obtener la categoría seleccionada del formulario
        categoria_id = request.POST.get('categoria')
        # Verificar si la categoría existe antes de obtenerla
        categoria = get_object_or_404(Categorias, id=categoria_id)
        # Actualizar la relación de categoría del post
        post.categoria.clear()
        post.categoria.add(categoria)

         # Actualizar la imagen del post
        if 'imagen' in request.FILES:
            # Eliminar la imagen anterior si existe
            if post.imagen:
                # Obtener la ruta de la imagen almacenada
                ruta_imagen = os.path.join(settings.MEDIA_ROOT, str(post.imagen))
                
                # Verificar si el archivo existe y eliminarlo
                if os.path.isfile(ruta_imagen):
                    os.remove(ruta_imagen)
            post.imagen = request.FILES['imagen']
        # Guardar los cambios en el post
        post.save()


        return HttpResponseRedirect(reverse('editar_post', kwargs={'post_id': post.id}))


@method_decorator(staff_member_required, name='dispatch')
class ListaCategorias(View):
    def get(self, request):
        lista_categorias = Categorias.objects.all()
        context = {
            'lista_categorias': lista_categorias
        }
        return render(request, 'Accounts/ListaCategorias.html', context)

# Clase con función para eliminar las categorias
class EliminarCat(View):
    def get(self,request, categoria_slug):
        categoria = get_object_or_404(Categorias, slug=categoria_slug)

        categoria.delete()
        return redirect('lista_categorias')
    
# Edita el titulo de las categorias  
@method_decorator(staff_member_required, name='dispatch')   
class EditarCategoria(View):
    def get(self, request, categoria_id):
        categoria = get_object_or_404(Categorias, id=categoria_id)
        return render(request, 'Accounts/Editarcategoria.html', {'categoria': categoria})

    def post(self, request, categoria_id):
        categoria = get_object_or_404(Categorias, id=categoria_id)
        nuevo_titulo = request.POST.get('titulo')

        # Comprobar si ya existe un slug con el nuevo título, Si existen categorías con el mismo slug, obtén el número máximo y suma uno
        slug = slugify(nuevo_titulo)
        existentes = Categorias.objects.filter(slug__startswith=slug)
        if existentes.exists():
            max_numero = existentes.aggregate(Max('slug'))
            siguiente_numero = int(max_numero['slug__max'][-1]) + 1
            slug = f"{slug}-{siguiente_numero}"
        
        # Actualizar el título y el slug de la categoría
        categoria.titulo = nuevo_titulo
        categoria.slug = slug
        categoria.save()
        
        return redirect('lista_categorias')
    
@method_decorator(staff_member_required, name='dispatch')   
class CrearCategoria(View):
    def get(self, request):
        return render(request, 'Accounts/CrearCategoria.html')

    def post(self, request):
        nuevo_titulo = request.POST.get('titulo')
        # Verificar si ya existe una categoría con el mismo título
        if Categorias.objects.filter(titulo=nuevo_titulo).exists():
            contador = 1
            # Si existe, agregar un número al final del título hasta que sea único
            while Categorias.objects.filter(titulo=nuevo_titulo).exists():
                nuevo_titulo = f"{request.POST.get('titulo')}_{contador}"
                contador += 1
        # Crear el slug igual al título
        slug = slugify(nuevo_titulo)
        # Crear la nueva categoría
        nueva_categoria = Categorias.objects.create(
            titulo=nuevo_titulo,
            slug=slug
        )

        
        return redirect('lista_categorias')