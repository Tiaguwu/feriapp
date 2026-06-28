"""Modelos de dominio para la aplicación de ferias."""

from __future__ import annotations
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.db import transaction

class Categoria(models.Model):
    """Categoría de una feria."""
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=False, null=False)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]
    
    def __str__(self):
        return self.nombre
    
    @classmethod
    def validate(cls, nombre, descripcion=""):
        """
        Valida los datos de la categoría.
        Retorna lista de errores (vacía si es válido).
        """
        errors = []
        
        if not nombre or not nombre.strip():
            errors.append("El nombre de la categoría es obligatorio.")
        
        if not descripcion or not descripcion.strip():
            errors.append("La descripción de la categoría es obligatoria.")
    

        return errors
    
    @classmethod
    def new(cls, nombre, descripcion=""):
        """
        Crea una nueva categoría si los datos son válidos.
        Retorna (instancia, errors).
        """
        errors = cls.validate(nombre, descripcion)
        if errors:
            return None, errors
        
        categoria = cls.objects.create(
            nombre=nombre.strip(),
            descripcion=descripcion.strip()
        )
        return categoria, []
    
    def update(self, nombre, descripcion=""):
        """
        Actualiza la categoría si los datos son válidos.
        Retorna lista de errores.
        """
        errors = self.__class__.validate(nombre, descripcion)
        if errors:
            return errors
        
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
        self.save()
        return []

class Feria(models.Model):
    """Representa una feria con su período, ubicación y capacidad disponible."""

    nombre = models.CharField(max_length=200)
    categorias = models.ManyToManyField(Categoria, related_name="ferias")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    ubicacion = models.CharField(max_length=200)
    capacidad_puestos = models.PositiveIntegerField()
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["fecha_inicio"]

    def __str__(self):
        """Retorna una representación legible de la feria."""
        return self.nombre

    def puestos_ocupados(self):
        """Retorna la cantidad de inscripciones confirmadas."""
        # Mientras Inscripcion no exista, no hay relaciones para contar.
        if not hasattr(self, "inscripcion_set"):
            return 0
        return self.inscripcion_set.filter(estado="confirmada").count()

    def puestos_disponibles(self):
        """Retorna los puestos libres."""
        return self.capacidad_puestos - self.puestos_ocupados()

    def tiene_lugar(self):
        """Retorna True si quedan puestos disponibles."""
        return self.puestos_disponibles() > 0

    @classmethod
    def validate(
        cls, nombre, categorias, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
):
        """
        Valida los datos de la feria.
        categorias: puede ser None, una lista de objetos Categoria, o un QuerySet.
        Retorna una lista de errores.
        """
        errors = []
    
        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")
    
        # Validar que tenga al menos una categoría
        if not categorias:
            errors.append("Debe seleccionar al menos una categoría.")
        elif hasattr(categorias, 'exists') and not categorias.exists():
            errors.append("Debe seleccionar al menos una categoría.")
        elif isinstance(categorias, (list, tuple)) and len(categorias) == 0:
            errors.append("Debe seleccionar al menos una categoría.")
    
        if not ubicacion or not ubicacion.strip():
            errors.append("La ubicación es obligatoria.")
    
        if capacidad_puestos is None or capacidad_puestos <= 0:
            errors.append("La capacidad de puestos debe ser mayor a cero.")
    
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            errors.append("La fecha de fin no puede ser anterior a la fecha de inicio.")
    
        return errors

    @classmethod
    def new(cls, nombre, categorias, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos):
        """
        Crea una nueva feria.
        categorias: puede ser una lista de objetos Categoria o un QuerySet.
        """
        errors = cls.validate(
            nombre, categorias, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
        )
        if errors:
            return None, errors
    
        feria = cls.objects.create(
            nombre=nombre.strip(),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            ubicacion=ubicacion.strip(),
            capacidad_puestos=capacidad_puestos,
        )
    
        # Agregar todas las categorías
        if categorias:
            feria.categorias.add(*categorias)  # El * desempaqueta la lista/QuerySet
    
        return feria, []

    def update(self, nombre, categorias, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos):
        """
        Actualiza una feria existente.
        categorias: puede ser una lista de objetos Categoria o un QuerySet.
        """
        errors = self.__class__.validate(
            nombre, categorias, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
        )
        if errors:
            return errors
    
        self.nombre = nombre.strip()
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.ubicacion = ubicacion.strip()
        self.capacidad_puestos = capacidad_puestos
    
        # Actualizar categorías
        if categorias is not None:
            self.categorias.clear()
            self.categorias.add(*categorias)
    
        self.save()
        return []

class Visitante(models.Model):
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'perfil_visitante')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Visitante"
        verbose_name_plural = "Visitantes"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido} {self.nombre}"
    
    @classmethod
    def validate(cls, nombre, apellido, email, usuario, exclude_pk=None):
        errors = []
        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")

        if not email or not email.strip():
            errors.append("El email es obligatorio.")
        elif cls.objects.filter(email=email.strip()).exclude(pk=exclude_pk).exists():
            errors.append("Ya existe un visitante registrado con ese email.")
        if not usuario:
            errors.append("El usuario asociado es obligatorio.")
        return errors

    @classmethod
    def new(cls, nombre, apellido, email, usuario):
        errors = cls.validate(nombre, apellido, email, usuario)
        if errors:
            return None, errors
        
        try:
            # Envolvemos la creación en un bloque atómico por seguridad transaccional
            with transaction.atomic():
                visitante = cls.objects.create(
                    nombre=nombre.strip(),
                    apellido=apellido.strip(),
                    email=email.strip(),
                    usuario=usuario
                )
                return visitante, []
        except Exception as e:
            return None, [f"Error interno de base de datos al guardar: {str(e)}"]

    def update(self, nombre, apellido, email):
        errors = self.__class__.validate(nombre, apellido, email, self.usuario, exclude_pk=self.pk)
        if errors:
            return errors
        
        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.email = email.strip()
        self.save()
        return []


class Emprendedor(models.Model):
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    rubro = models.CharField(max_length=200)
    telefono = models.CharField(max_length=17, blank=True, null=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'perfil_emprendedor')

    class Meta:
        verbose_name = "Emprendedor"
        verbose_name_plural = "Emprendedores"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido} {self.nombre}"
    
    @classmethod
    def validate(cls, nombre, apellido, email, rubro, telefono, usuario, exclude_pk=None):
        errors = []
        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")

        if not email or not email.strip():
            errors.append("El email es obligatorio.")
        elif cls.objects.filter(email=email.strip()).exclude(pk=exclude_pk).exists():
            errors.append("Ya existe un emprendedor registrado con ese email.")

        if not rubro or not rubro.strip():
            errors.append("El rubro es obligatorio.")
        if not telefono or not telefono.strip():
            errors.append("El telefono es obligatorio.")
        if not usuario:
            errors.append("El usuario asociado es obligatorio.")
        return errors

    @classmethod
    def new(cls, nombre, apellido, email, rubro, telefono, usuario):
        errors = cls.validate(nombre, apellido, email, rubro, telefono, usuario)
        if errors:
            return None, errors
        
        try:
            # Envolvemos la creación en un bloque atómico por seguridad transaccional
            with transaction.atomic():
                emprendedor = cls.objects.create(
                    nombre=nombre.strip(),
                    apellido=apellido.strip(),
                    email=email.strip(),
                    rubro=rubro.strip(),
                    telefono=telefono.strip(),
                    usuario=usuario,
                )
                return emprendedor, []
        except Exception as e:
            return None, [f"Error interno de base de datos al guardar: {str(e)}"]

    def update(self, nombre, apellido, email, rubro, telefono):
        errors = self.__class__.validate(nombre, apellido, email, rubro, telefono, self.usuario, exclude_pk=self.pk)
        if errors:
            return errors
        
        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.email = email.strip()
        self.rubro = rubro.strip()
        self.telefono = telefono.strip()
        self.save()
        return []

class Inscripcion(models.Model):
    """Representa la inscripicón de un emprendedor a una feria."""

    ESTADOS = [
        ("lista_espera", "En lista de espera"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
    ]

    emprendedor = models.ForeignKey(Emprendedor, on_delete=models.CASCADE)
    feria = models.ForeignKey(Feria, on_delete=models.CASCADE)
    numero_puesto = models.PositiveIntegerField(null=True, blank=True)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(choices=ESTADOS, default="lista_espera", max_length=15)
    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        unique_together = ("emprendedor", "feria")
        ordering = ["-fecha_inscripcion"]

    def __str__(self):
        """Retorna una representación legible de la inscripción."""
        return f"Inscripción de {self.emprendedor} a {self.feria}. Puesto: {self.numero_puesto or 'N/A'} - Estado: {self.estado}"

    @classmethod
    def validate(
        cls, emprendedor, feria,registrado_por
    ):
        """
        Valida los datos de la inscripción. Retorna una lista de errores.
        Si la lista está vacía, los datos son válidos.
        """
        errors = []

        if not emprendedor:
            errors.append("Debe seleccionar un emprendedor.")

        if not feria:
            errors.append("Debe seleccionar una feria.")

        if not registrado_por:
            errors.append("Debe haber un usuario registrado que realice la inscripción.")

        if feria and not feria.activa:
            errors.append("La feria no está activa.")

        if feria and date.today() > feria.fecha_fin:
            errors.append("La feria ya terminó.")

        if emprendedor and feria:
            ya_inscripto = Inscripcion.objects.filter(
                emprendedor=emprendedor,
                feria=feria
            ).exclude(estado='cancelada').exists() # Permite reactivar una cancelada
            if ya_inscripto:
                errors.append("Ya estás inscripto en esta feria.")

        return errors

    @classmethod
    def puesto_libre(cls, feria):
        """Retorna el número del primer puesto libre en la feria."""
        puestos_tomados = set(
            feria.inscripcion_set
                .select_for_update()
                .filter(estado='confirmada')
                .values_list('numero_puesto', flat=True)
        )
        for puesto in range(1, feria.capacidad_puestos + 1):
            if puesto not in puestos_tomados:
                return puesto
        return None

    @classmethod
    def new(
        cls, emprendedor, feria, registrado_por
    ):
        """
        Crea y persiste una nueva inscripción si los datos son válidos.
        Retorna (instancia, errors). Si hay errores, instancia es None.
        """
        errors = cls.validate(
            emprendedor, feria, registrado_por
        )

        if errors:
            return None, errors

        with transaction.atomic():
            hay_lugar = feria.tiene_lugar()

            inscripcion_cancelada = cls.objects.filter(
                emprendedor=emprendedor,
                feria=feria,
                estado='cancelada'
            ).first()

            # Si hay una cancelada, la reactivamos
            if inscripcion_cancelada:
                inscripcion_cancelada.estado = 'confirmada' if hay_lugar else 'lista_espera'
                inscripcion_cancelada.numero_puesto = cls.puesto_libre(feria) if hay_lugar else None
                inscripcion_cancelada.registrado_por = registrado_por
                inscripcion_cancelada.save()
                return inscripcion_cancelada, []

            inscripcion = cls.objects.create(
                emprendedor=emprendedor,
                numero_puesto=cls.puesto_libre(feria) if hay_lugar else None,
                feria=feria,
                registrado_por=registrado_por,
                estado='confirmada' if hay_lugar else 'lista_espera',
            )
        return inscripcion, []

    def update(
        self, nuevo_estado                  
    ):
        """
        Actualiza el estado de la inscripción y ajusta los puestos si es necesario.
        Retorna una lista de errores. Si está vacía, la actualización fue exitosa.
        """
        # Validar el nuevo estado
        estados_validos = [e[0] for e in self.ESTADOS]
        if nuevo_estado not in estados_validos:
            return [f"El estado: '{nuevo_estado}' no es válido."]

        with transaction.atomic():
            if nuevo_estado == 'confirmada' and self.estado != 'confirmada':
                # Solo confirmar si hay lugar
                if self.feria.tiene_lugar():
                    self.estado = 'confirmada'
                    self.numero_puesto = Inscripcion.puesto_libre(self.feria)
                    self.save()
                else:
                    return ["No hay puestos disponibles para confirmar esta inscripción."]
            elif nuevo_estado == 'cancelada' and self.estado == 'confirmada':
                # Liberar el puesto si se cancela una inscripción confirmada
                self.estado = 'cancelada'
                self.save()
                # Intentar confirmar la siguiente inscripción en lista de espera
                siguiente = (
                    Inscripcion.objects
                    .select_for_update()
                    .filter(feria=self.feria, estado='lista_espera')
                    .order_by('fecha_inscripcion')
                    .first()
                )
                if siguiente:
                    siguiente.estado = 'confirmada'
                    siguiente.numero_puesto = Inscripcion.puesto_libre(self.feria)
                    siguiente.save()
            else:
                self.estado = nuevo_estado
                self.save()
        return []

class Resenia(models.Model):
    """Representa una reseña de un visitante sobre una feria."""

    emprendedor = models.ForeignKey(Emprendedor, on_delete=models.CASCADE)
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE)
    feria = models.ForeignKey(Feria, on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField()  # 1 a 5
    comentario = models.TextField(blank=True, null=True)
    fecha_resenia = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        unique_together = ('visitante', 'feria', 'emprendedor')
        ordering = ['-fecha_resenia']

    def __str__(self):
        return f"Reseña de {self.visitante} sobre {self.feria}/{self.emprendedor}: {self.calificacion} estrellas"

    def validar_puntaje(self):
        """Valida que la calificación esté entre 1 y 5."""
        if not (1 <= self.calificacion <= 5):
            raise ValueError("La calificación debe estar entre 1 y 5.")

    @classmethod
    def validate(cls, emprendedor, visitante, feria, calificacion):
        errors = []
        if not emprendedor:
            errors.append("Debe seleccionar un emprendedor.")
        if not visitante:
            errors.append("Debe seleccionar un visitante.")
        if not feria:
            errors.append("Debe seleccionar una feria.")
        if calificacion is None or not (1 <= calificacion <= 5):
            errors.append("La calificación debe estar entre 1 y 5.")
        # Verificamos que el emprendedor tenga una inscripción confirmada en la feria
        if emprendedor and feria:
            if not Inscripcion.objects.filter(
                emprendedor=emprendedor,
                feria=feria,
                estado='confirmada'
            ).exists():
                errors.append("El emprendedor no tiene una inscripción confirmada en esta feria.")
        # Verificamos que no haya reseña previa del mismo visitante para la misma feria y emprendedor
        if emprendedor and visitante:
            if cls.objects.filter(
                emprendedor=emprendedor,
                visitante=visitante,
                feria=feria
            ).exists():
                errors.append("Ya existe una reseña de este visitante para esta feria y emprendedor.")

        # Verificamos que la feria este activa o ya haya pasado
        if feria and date.today() < feria.fecha_inicio:
            errors.append("La feria aún no ha comenzado.")
        return errors

    @classmethod
    def new(cls, emprendedor, visitante, feria, calificacion, comentario=""):
        errors = cls.validate(emprendedor, visitante, feria, calificacion)
        if errors:
            return None, errors
        
        resenia = cls.objects.create(
            emprendedor=emprendedor,
            visitante=visitante,
            feria=feria,
            calificacion=calificacion,
            comentario=comentario.strip() if comentario else ""
        )
        return resenia, []