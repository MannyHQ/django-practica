"""
URL configuration for crud_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from crud import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name="index"),
    path('addnew',views.addnew,name="addnew"),
    path('edit/<int:id>',views.edit,name="edit"),
    path('update/<int:id>',views.update,name="update"),
    path('delete/<int:id>',views.destroy,name="destroy"),
    path('signup',views.signup,name="signup"),
    path('signout',views.signout,name="signout"),
    path('signin',views.signin,name="signin"),
    path('correo/<str:correo>',views.enviar_correo,name="correo"),
    path('solicitud',views.solicitud,name="solicitud"),
    path('correo_solicitud/<int:id>',views.enviar_solicitud,name="correo_solicitud"),
    path('egresados',views.egresados,name="egresados"),
    path('egresados_pdf',views.egresados_pdf,name="egresados_pdf"),
    path('solicitud_filtro',views.solicitudes_servicio,name="solicitud_filtro"),
    path('solicitud_servicio_pdf/<int:solicitud_id>',views.solicitud_servicio_pdf,name="solicitud_servicio_pdf"),
    path('solicitud_servicio_general_pdf',views.solicitud_servicio_general_pdf,name="solicitud_servicio_general_pdf"),
    path('empresas',views.empresas,name="empresas"),
    path('exportar_empresas_pdf',views.exportar_empresas_pdf,name="exportar_empresas_pdf"),
    path('ocupaciones',views.lista_ocupaciones,name="ocupaciones"),
    path('exportar_ocupaciones_pdf',views.exportar_ocupaciones_pdf,name="exportar_ocupaciones_pdf")
]
