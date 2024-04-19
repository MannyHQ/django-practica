from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Empleado(models.Model):
    nombre = models.CharField(max_length=50)
    correo = models.EmailField()
    telefono = models.CharField(max_length=10)

    class Meta:
        db_table = "tblempleado"



class Prueba(models.Model):
    id_empleado = models.ForeignKey(Empleado,on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=40)

class Ocupacion(models.Model):
    id_ocupacion = models.AutoField(primary_key=True)
    nombre_ocupacion = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_ocupacion

class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nombre_empresa = models.CharField(max_length=30)
    direccion_empresa = models.CharField(max_length=100)
    telefono_empresa = models.CharField(max_length=10)
    email_empresa = models.EmailField(max_length=100)

    def __str__(self):
        return self.nombre_empresa

class Egresado(models.Model):
    id_egresado = models.AutoField(primary_key=True)
    nombre_egresado = models.CharField(max_length=30)
    apellido_egresado = models.CharField(max_length=30)
    direccion_egresado = models.CharField(max_length=100)
    telefono_egresado = models.CharField(max_length=10)
    email_egresado = models.EmailField(max_length=100)
    ocupacion = models.ForeignKey(Ocupacion, on_delete=models.CASCADE)
    estatus_egresado = models.BooleanField()

    def __str__(self):
        return self.nombre_egresado

class SolicitudServicio(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    fecha_solicitud = models.DateField()
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    ocupacion = models.ForeignKey(Ocupacion, on_delete=models.CASCADE)
    perfil_solicitud = models.TextField()
    estatus_solicitud = models.BooleanField()
    id_usuario = models.CharField(max_length=20)

class DetalleSolicitud(models.Model):
    id_solicitud = models.ForeignKey(SolicitudServicio, on_delete=models.CASCADE)
    id_egresado = models.ForeignKey(Egresado, on_delete=models.CASCADE)
    estatus_detalle = models.BooleanField()

@receiver(post_save, sender=Empleado)
def crear_detalle_solicitud(sender, instance, created, **kwargs):
    if created:
        empleado = Empleado.objects.filter(Q(correo=instance.correo))
        for emp in empleado:
            print(emp.nombre)
            Prueba.objects.create(id_empleado=instance, descripcion=emp.nombre)

@receiver(post_save, sender=SolicitudServicio)
def crear_detalle_solicitud(sender, instance, created, **kwargs):
    if created:
        egresado = Egresado.objects.filter(Q(ocupacion=instance.ocupacion))
        for egr in egresado:
            print(egr.nombre_egresado)
            DetalleSolicitud.objects.create(id_solicitud=instance,id_egresado=egr,estatus_detalle=1)
            #Prueba.objects.create(id_empleado=instance, descripcion=emp.nombre)