from django.shortcuts import redirect, render
from crud.forms import EmpleadoForm, SolicitudServicioForm
from crud.models import Empleado, SolicitudServicio, DetalleSolicitud, Empresa, Egresado, Ocupacion
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime
# Create your views here.


def enviar_correo(request,correo):
    subject = "Prueba de envio de correo desde Django"
    message = "Esto es una prueba para enviar un correo desde Django para futuros desarrollos!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['manuelisidrogh@gmail.com']
    send_mail(subject,message,from_email,recipient_list)
    return redirect('/')

def enviar_solicitud(request,id):
    solicitud = SolicitudServicio.objects.get(id_solicitud=id)
    empresa = Empresa.objects.get(id_empresa=solicitud.empresa.id_empresa)
    dsolicitud = DetalleSolicitud.objects.filter(Q(id_solicitud=solicitud))
    lista_correo_egresados = []
    for ds in dsolicitud:
        print(ds.id_egresado.email_egresado)
        lista_correo_egresados.append(ds.id_egresado.email_egresado)
    print(empresa.nombre_empresa,'-',empresa.email_empresa)
    print(lista_correo_egresados)
    enviar_empresa(empresa.email_empresa)
    enviar_egresados(lista_correo_egresados)
    return redirect('solicitud')

def enviar_empresa(correo):
    subject = "Prueba de envio de correo desde Django"
    message = "Esto es una prueba para enviar un correo desde Django para futuros desarrollos!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [correo]
    send_mail(subject,message,from_email,recipient_list)

def enviar_egresados(correo = []):
    subject = "Prueba de envio de correo desde Django"
    message = "Esto es una prueba para enviar un correo desde Django para futuros desarrollos!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = correo
    send_mail(subject,message,from_email,recipient_list)

@login_required(login_url='signin')
def solicitud(request):
    solicitudes = SolicitudServicio.objects.all()
    if request.method == "POST":
        form = SolicitudServicioForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.fecha_solicitud = timezone.now().date()
            solicitud.id_usuario = request.user.username
            solicitud.save()
            print("Nombre de usuario:",request.user.username)
            return redirect('solicitud')
    else:
        form = SolicitudServicioForm()
    context = {
        'form':form,
        'solicitudes': solicitudes
    }
    return render(request,'solicitud.html',context)

def signin(request):
    if request.user.is_authenticated:
        return render(request,'/')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('/')
        else:
            msg = 'Error login'
            form = AuthenticationForm(request.POST)
            return render(request,'login.html',{'form':form,'msg':msg})
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form
    }
    return render(request,'login.html',context)

def signout(request):
    logout(request)
    return redirect('/')

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username,password=password)
            login(request,user)
            return redirect("/")
        else:
            return render(request,"signup.html",{'form':form})
    else:
        form = UserCreationForm()
    context = {
        'form': form,
    }    
    return render(request,'signup.html', context)

def destroy(request,id):
    empleado = Empleado.objects.get(id=id)
    empleado.delete()
    return redirect('/')

def update(request,id):
    empleado = Empleado.objects.get(id=id)
    form = EmpleadoForm(request.POST, instance=empleado)
    if form.is_valid():
        form.save()
        return redirect('/')
    return render(request,'edit.html',{'empleado':empleado})

@login_required(login_url='signin')
def edit(request,id):
    empleado = Empleado.objects.get(id=id)
    context = {
        'empleado': empleado
    }
    return render(request,'edit.html',context)

@login_required(login_url='signin')
def addnew(request):
    if request.method == "POST":
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                #print(request.POST.get('correo'))
                #empleados = Empleado.objects.filter(Q(correo__icontains=request.POST.get('correo')))
                #for empleado in empleados:
                #    print(empleado.nombre)
                return redirect('/')
            except:
                pass
    else:
        form = EmpleadoForm()

    context = {
        'form': form,
    }
    return render(request,'index.html',context)

@login_required(login_url='signin')
def index(request):
    empleados = Empleado.objects.all()
    context = {
        'empleados': empleados
    }
    return render(request,'show.html',context)

def egresados(request):
    ocupaciones = Ocupacion.objects.all()
    estados = Egresado.objects.values_list('estatus_egresado', flat=True).distinct()
    
    if request.method == "GET":
        filtro_ocupacion = request.GET.get('ocupacion')
        filtro_estado = request.GET.get('estado')
        filtro_telefono = request.GET.get('telefono')
        filtro_email = request.GET.get('email')
        filtro_nombre = request.GET.get('nombre')
        filtro_apellido = request.GET.get('apellido')

        request.session['egresado_ocupacion'] = filtro_ocupacion
        request.session['egresado_estado'] = filtro_estado
        request.session['egresado_telefono'] = filtro_telefono
        request.session['egresado_email'] = filtro_email
        request.session['egresado_nombre'] = filtro_nombre
        request.session['egresado_apellido'] = filtro_apellido

        egresados = Egresado.objects.all()

        if filtro_ocupacion:
            egresados = egresados.filter(ocupacion__nombre_ocupacion=filtro_ocupacion)
        
        if filtro_estado:
            egresados = egresados.filter(estatus_egresado=filtro_estado)
        
        if filtro_telefono:
            egresados = egresados.filter(telefono_egresado__icontains=filtro_telefono)
        
        if filtro_email:
            egresados = egresados.filter(email_egresado__icontains=filtro_email)

        if filtro_nombre:
            egresados = egresados.filter(nombre_egresado__icontains=filtro_nombre)
        
        if filtro_apellido:
            egresados = egresados.filter(apellido_egresado__icontains=filtro_apellido)

    context = {
        'egresados': egresados,
        'ocupaciones': ocupaciones,
        'estados': estados
    }
    return render(request, 'egresados.html', context)

def solicitudes_servicio(request):
    empresas = Empresa.objects.all()
    ocupaciones = Ocupacion.objects.all()
    estados = SolicitudServicio.objects.values_list('estatus_solicitud', flat=True).distinct()
    
    if request.method == "GET":
        filtro_empresa = request.GET.get('empresa')
        filtro_ocupacion = request.GET.get('ocupacion')
        filtro_estado = request.GET.get('estado')
        filtro_fecha_solicitud = request.GET.get('fecha_solicitud')

        request.session['solicitud_empresa']  = request.GET.get('empresa')
        request.session['solicitud_ocupacion'] = request.GET.get('ocupacion')     
        request.session['solicitud_estado'] = request.GET.get('estado')
        request.session['solicitud_fecha'] = request.GET.get('fecha_solicitud')

        solicitudes = SolicitudServicio.objects.all()

        if filtro_empresa:
            solicitudes = solicitudes.filter(empresa=filtro_empresa)
            
        
        if filtro_ocupacion:
            solicitudes = solicitudes.filter(ocupacion=filtro_ocupacion)
            
        
        if filtro_estado:
            solicitudes = solicitudes.filter(estatus_solicitud=filtro_estado)
            

        if filtro_fecha_solicitud:
            fecha_solicitud = datetime.strptime(filtro_fecha_solicitud, '%Y-%m-%d').date()
            solicitudes = solicitudes.filter(fecha_solicitud = fecha_solicitud)
            

    context = {
        'solicitudes': solicitudes,
        'empresas': empresas,
        'ocupaciones': ocupaciones,
        'estados': estados
    }
    return render(request, 'solicitud_filtro.html', context)

def solicitud_servicio_pdf(request, solicitud_id):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="solicitud_servicio_{solicitud_id}.pdf"'

    # Creamos un objeto PDF
    p = canvas.Canvas(response)

    # Establecemos el encabezado
    p.setFont("Helvetica", 16)
    p.drawString(100, 800, "Reporte de Solicitud de Servicio con Egresados")

    # Obtenemos la solicitud de servicio y sus detalles
    solicitud = SolicitudServicio.objects.get(id_solicitud=solicitud_id)
    detalles_solicitud = DetalleSolicitud.objects.filter(id_solicitud=solicitud_id)

    # Mostramos la información de la solicitud
    p.drawString(100, 750, f"Fecha Solicitud: {solicitud.fecha_solicitud}")
    p.drawString(100, 730, f"Empresa: {solicitud.empresa.nombre_empresa}")
    p.drawString(100, 710, f"Ocupación: {solicitud.ocupacion.nombre_ocupacion}")
    p.drawString(100, 690, f"Perfil Solicitud: {solicitud.perfil_solicitud}")
    p.drawString(100, 670, f"Estado: {solicitud.estatus_solicitud}")

    p.drawString(100, 650, "")  # Salto de línea
    # Mostramos los detalles de los egresados asociados a la solicitud
    p.drawString(100, 630, "Egresados que cumplen con el perfil:")
    y = 600
    # Añadimos un espacio entre la información de la solicitud y los egresados

    egresados_correos = []

    for detalle in detalles_solicitud:
        egresado = detalle.id_egresado
        p.drawString(120, y, f"Egresado: {egresado.nombre_egresado} {egresado.apellido_egresado}")
        p.drawString(120, y - 20, f"Correo: {egresado.email_egresado}")
        p.drawString(120, y - 40, f"Teléfono: {egresado.telefono_egresado}")
        p.drawString(120, y - 60, f"Ocupación: {egresado.ocupacion.nombre_ocupacion}")
        egresados_correos.append(egresado.email_egresado)
        y -= 80

        p.drawString(100, y, "")  # Salto de línea

        y -= 20  # Espacio entre egresados

    # Guardamos el PDF
    p.showPage()
    p.save()
    
    if egresados_correos.count != 0:
        asunto = 'Oferta laboral'
        cuerpo_correo = 'Ha sido elegido para participar en el proceso de seleccion por parte de la empresa: '+solicitud.empresa.nombre_empresa
        remitente = settings.EMAIL_HOST_USER
        destinatario = egresados_correos
        enviar_correo(asunto,cuerpo_correo,remitente,destinatario,'archivo.pdf',response.getvalue(),'application/pdf')


    # Configurar el correo electrónico
    asunto = 'Adjunto: Reporte de egresados que cumplen'
    cuerpo_correo = 'Archivo pdf con los egresados que cumplen con la solicitud'
    remitente = settings.EMAIL_HOST_USER
    destinatario = [solicitud.empresa.email_empresa]
    enviar_correo(asunto,cuerpo_correo,remitente,destinatario,'archivo.pdf',response.getvalue(),'application/pdf')

    # # Creamos un mensaje de correo electrónico
    # email = EmailMessage(
    #     asunto,
    #     cuerpo_correo,
    #     remitente,
    #     destinatario
    # )

    # # Adjuntamos el archivo PDF al mensaje de correo electrónico
    # email.attach('archivo.pdf', response.getvalue(), 'application/pdf')

    # # Enviamos el correo electrónico
    # email.send()
    return response


def enviar_correo(asunto,cuerpo_correo,remitente,destinatario, nombre_archivo,response,tipo_archivo):
    email = EmailMessage(asunto,cuerpo_correo,remitente,destinatario)
    email.attach(nombre_archivo,response,tipo_archivo)
    email.send()



def solicitud_servicio_general_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="solicitudes_servicio.pdf"'

    # Creamos un objeto PDF
    p = canvas.Canvas(response)

    # Establecemos el encabezado
    p.setFont("Helvetica", 16)
    p.drawString(100, 800, "Reporte de Solicitudes de Servicio con Egresados")

    # Obtenemos los parámetros de filtro del request GET
    filtro_empresa = request.session.get('solicitud_empresa')
    filtro_ocupacion = request.session.get('solicitud_ocupacion')
    filtro_estado = request.session.get('solicitud_estado')
    filtro_fecha_solicitud = request.session.get('solicitud_fecha')

    # Filtramos las solicitudes según los parámetros de filtro
    solicitudes = SolicitudServicio.objects.all()

    if filtro_empresa:
        solicitudes = solicitudes.filter(empresa=filtro_empresa)
    if filtro_ocupacion:
        solicitudes = solicitudes.filter(ocupacion=filtro_ocupacion)
    if filtro_estado:
        solicitudes = solicitudes.filter(estatus_solicitud=filtro_estado)
    if filtro_fecha_solicitud:
        fecha_solicitud = datetime.strptime(filtro_fecha_solicitud, '%Y-%m-%d').date()
        solicitudes = solicitudes.filter(fecha_solicitud=fecha_solicitud)

    # Mostramos la información de las solicitudes
    y = 750
    for solicitud in solicitudes:
        p.drawString(100, y, f"Fecha Solicitud: {solicitud.fecha_solicitud}")
        p.drawString(100, y - 20, f"Empresa: {solicitud.empresa.nombre_empresa}")
        p.drawString(100, y - 40, f"Ocupación: {solicitud.ocupacion.nombre_ocupacion}")
        p.drawString(100, y - 60, f"Perfil Solicitud: {solicitud.perfil_solicitud}")
        p.drawString(100, y - 80, f"Estado: {solicitud.estatus_solicitud}")

        # Obtenemos los detalles de los egresados asociados a la solicitud
        detalles_solicitud = DetalleSolicitud.objects.filter(id_solicitud=solicitud.id_solicitud)
        p.drawString(100, y - 100, "Egresados que cumplen con el perfil:")
        detalle_y = y - 120
        for detalle in detalles_solicitud:
            egresado = detalle.id_egresado
            p.drawString(120, detalle_y, f"Egresado: {egresado.nombre_egresado} {egresado.apellido_egresado}")
            p.drawString(120, detalle_y - 20, f"Correo: {egresado.email_egresado}")
            p.drawString(120, detalle_y - 40, f"Teléfono: {egresado.telefono_egresado}")
            p.drawString(120, detalle_y - 60, f"Ocupación: {egresado.ocupacion.nombre_ocupacion}")
            detalle_y -= 80

        y -= 200  # Añadimos espacio entre las solicitudes
        p.drawString(100, y, "")  # Salto de línea
        y -= 100
        p.drawString(100, y, "")  # Salto de línea

    # Guardamos el PDF
    p.showPage()
    p.save()

    return response

def egresados_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="egresados.pdf"'

    # Creamos un objeto PDF
    p = canvas.Canvas(response)
    p.setFont("Helvetica", 16)
    p.drawString(100, 800, "Reporte de Egresados")

    # Obtenemos los parámetros de filtrado
    filtro_ocupacion = request.session.get('egresado_ocupacion')
    filtro_estado = request.session.get('egresado_estado')
    filtro_telefono = request.session.get('egresado_telefono')
    filtro_email = request.session.get('egresado_email')
    filtro_nombre = request.session.get('egresado_nombre')
    filtro_apellido = request.session.get('egresado_apellido')

    # Filtramos los egresados según los parámetros
    egresados = Egresado.objects.all()

    if filtro_ocupacion:
        egresados = egresados.filter(ocupacion__nombre_ocupacion=filtro_ocupacion)
    
    if filtro_estado:
        egresados = egresados.filter(estatus_egresado=filtro_estado)

    if filtro_telefono:
        egresados = egresados.filter(telefono_egresado__icontains = filtro_telefono)

    if filtro_email:
        egresados = egresados.filter(email_egresado__icontains = filtro_email)

    if filtro_nombre:
        egresados = egresados.filter(nombre_egresado__icontains = filtro_nombre)

    if filtro_apellido:
        egresados = egresados.filter(apellido_egresado__icontains = filtro_apellido)
        
    # Añadimos los datos de los egresados al PDF
    y = 750
    espacio_entre_egresados = 150

    # Recorrer todos los egresados
    for egresado in egresados:
        # Agregar cada línea de información del egresado
        p.drawString(100, y, f"Nombre: {egresado.nombre_egresado}")
        p.drawString(100, y - 20, f"Apellido: {egresado.apellido_egresado}")
        p.drawString(100, y - 40, f"Telefono: {egresado.telefono_egresado}")
        p.drawString(100, y - 60, f"Email: {egresado.email_egresado}")
        p.drawString(100, y - 80, f"Ocupación: {egresado.ocupacion.nombre_ocupacion}")
        p.drawString(100, y - 100, f"Estado: {egresado.estatus_egresado}")

        # Ajustar la posición vertical para el siguiente egresado
        y -= espacio_entre_egresados  # Espacio entre egresados

        # Agregar espacio adicional entre egresados
        y -= 20

    # Guardamos el PDF
    p.showPage()
    p.save()

    return response


def empresas(request):
    # Obtener todas las empresas
    empresas = Empresa.objects.all()

    # Filtrar las empresas por nombre, teléfono y correo electrónico si se envió un formulario de filtro
    if request.method == "GET":
        filtro_nombre = request.GET.get('nombre')
        filtro_telefono = request.GET.get('telefono')
        filtro_email = request.GET.get('email')

        empresa_nombre = filtro_nombre
        empresa_email = filtro_email
        empresa_telefono = filtro_telefono

        request.session['empresa_nombre'] = empresa_nombre
        request.session['empresa_telefono'] = empresa_telefono
        request.session['empresa_email'] = empresa_email

        if filtro_nombre:
            empresas = empresas.filter(nombre_empresa__icontains=filtro_nombre)
        
        if filtro_telefono:
            empresas = empresas.filter(telefono_empresa__icontains=filtro_telefono)
        
        if filtro_email:
            empresas = empresas.filter(email_empresa__icontains=filtro_email)


    context = {
        'empresas': empresas
    }
    return render(request, 'empresas.html', context)


def exportar_empresas_pdf(request):
    # Crear el objeto PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="empresas.pdf"'
    p = canvas.Canvas(response)

    # Encabezado del PDF
    p.setFont("Helvetica", 16)
    p.drawString(100, 800, "Listado de Empresas")
    # Obtener los parámetros de filtro del request GET
    filtro_nombre = request.session.get('empresa_nombre')
    filtro_telefono = request.session.get('empresa_telefono')
    filtro_email = request.session.get('empresa_email')
    

    # Filtrar las empresas según los parámetros de filtro
    empresas = Empresa.objects.all()
    print(f"Filtro Nombre: {filtro_nombre}")
    print(f"Filtro Teléfono: {filtro_telefono}")
    print(f"Filtro Email: {filtro_email}")

    if filtro_nombre:
        empresas = empresas.filter(nombre_empresa__icontains=filtro_nombre)

    if filtro_telefono:
        empresas = empresas.filter(telefono_empresa__icontains=filtro_telefono)
 
    if filtro_email:
        empresas = empresas.filter(email_empresa__icontains=filtro_email)


    # Mostrar los detalles de las empresas
    y = 750  # Posición inicial para las empresas
    for empresa in empresas:
        # Mostrar los detalles de la empresa
        p.drawString(100, y, f"Nombre: {empresa.nombre_empresa}")
        p.drawString(100, y - 20, f"Dirección: {empresa.direccion_empresa}")
        p.drawString(100, y - 40, f"Teléfono: {empresa.telefono_empresa}")
        p.drawString(100, y - 60, f"Correo Electrónico: {empresa.email_empresa}")
        y -= 80  # Añadir espacio entre empresas
        p.drawString(100, y, "")  # Salto de línea

        y -= 20  # Espacio entre empresas
    # Guardar el PDF
    p.showPage()
    p.save()

    return response


def lista_ocupaciones(request):
    # Obtener el parámetro de filtro del request GET
    filtro_nombre_ocupacion = request.GET.get('nombre_ocupacion')
    request.session['ocupaciones'] = filtro_nombre_ocupacion

    # Filtrar las ocupaciones según el parámetro de filtro
    ocupaciones = Ocupacion.objects.all()
    if filtro_nombre_ocupacion:
        ocupaciones = ocupaciones.filter(nombre_ocupacion__icontains=filtro_nombre_ocupacion)
        

    context = {
        'ocupaciones': ocupaciones
    }
    return render(request, 'ocupaciones.html', context)

def exportar_ocupaciones_pdf(request):
    # Obtener el parámetro de filtro del request GET
    filtro_nombre_ocupacion = request.session.get('ocupaciones')

    # Filtrar las ocupaciones según el parámetro de filtro
    ocupaciones = Ocupacion.objects.all()
    if filtro_nombre_ocupacion:
        ocupaciones = ocupaciones.filter(nombre_ocupacion__icontains=filtro_nombre_ocupacion)

    # Crear el objeto PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ocupaciones.pdf"'
    p = canvas.Canvas(response)

    # Encabezado del PDF
    p.setFont("Helvetica", 16)
    p.drawString(100, 800, "Listado de Ocupaciones")

    # Mostrar los detalles de las ocupaciones
    y = 750  # Posición inicial para las ocupaciones
    for ocupacion in ocupaciones:
        # Mostrar los detalles de la ocupación
        p.drawString(100, y, f"Nombre: {ocupacion.nombre_ocupacion}")
        y -= 20  # Añadir espacio entre ocupaciones

    # Guardar el PDF
    p.showPage()
    p.save()

    return response