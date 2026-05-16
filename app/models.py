"""Modelos de dominio para la aplicación de ferias."""

from __future__ import annotations

from django.db import models
from django.contrib.auth.models import User
from django.db import transaction


class Feria(models.Model):
    """Representa una feria con su período, ubicación y capacidad disponible."""

    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
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
        cls, nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
    ):
        """
        Valida los datos de la feria. Retorna una lista de errores.
        Si la lista está vacía, los datos son válidos.
        """
        errors = []

        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")

        if not categoria or not categoria.strip():
            errors.append("La categoría es obligatoria.")

        if not ubicacion or not ubicacion.strip():
            errors.append("La ubicación es obligatoria.")

        if capacidad_puestos is None or capacidad_puestos <= 0:
            errors.append("La capacidad de puestos debe ser mayor a cero.")

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            errors.append("La fecha de fin no puede ser anterior a la fecha de inicio.")

        return errors

    @classmethod
    def new(
        cls, nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
    ):
        """
        Crea y persiste una nueva feria si los datos son válidos.
        Retorna (instancia, errors). Si hay errores, instancia es None.
        """
        errors = cls.validate(
            nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
        )
        if errors:
            return None, errors

        feria = cls.objects.create(
            nombre=nombre.strip(),
            categoria=categoria.strip(),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            ubicacion=ubicacion.strip(),
            capacidad_puestos=capacidad_puestos,
        )
        return feria, []

    def update(
        self, nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
    ):
        """
        Actualiza los datos de la feria si los datos son válidos.
        Retorna una lista de errores. Si está vacía, la actualización fue exitosa.
        """
        errors = self.__class__.validate(
            nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
        )
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.categoria = categoria.strip()
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.ubicacion = ubicacion.strip()
        self.capacidad_puestos = capacidad_puestos
        self.save()
        return []

class Visitante(models.Model):
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Visitante"
        verbose_name_plural = "Visitantes"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido} {self.nombre}"
    
    @classmethod
    def validate(cls, nombre, apellido, email, usuario):
        errors = []
        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")
        if not email or not email.strip():
            errors.append("El email es obligatorio.")
        if not usuario:
            errors.append("El usuario asociado es obligatorio.")
        return errors

    @classmethod
    def new(cls, nombre, apellido, email, usuario):
        errors = cls.validate(nombre, apellido, email, usuario)
        if errors:
            return None, errors
        
        visitante = cls.objects.create(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            email=email.strip(),
            usuario=usuario
        )
        return visitante, []

    def update(self, nombre, apellido, email):
        errors = self.__class__.validate(nombre, apellido, email, self.usuario)
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
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Emprendedor"
        verbose_name_plural = "Emprendedores"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido} {self.nombre}"
    
    @classmethod
    def validate(cls, nombre, apellido, email, rubro, telefono, usuario):
        errors = []
        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")
        if not email or not email.strip():
            errors.append("El email es obligatorio.")
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
        
        emprendedor = cls.objects.create(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            email=email.strip(),
            rubro=rubro.strip(),
            telefono=telefono.strip(),
            usuario=usuario,
        )
        return emprendedor, []

    def update(self, nombre, apellido, email, rubro, telefono):
        errors = self.__class__.validate(nombre, apellido, email, rubro, telefono, self.usuario)
        if errors:
            return errors
        
        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.email = email.strip()
        self.rubro = rubro.strip()
        self.telefono = telefono.strip()
        self.save()
        return []

    # class Categoria(models.Model): ...  ← extraer categoria a FK
    # class Emprendedor(models.Model): ...
    # class Inscripcion(models.Model):
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
        return f"Inscripción de {self.emprendedor} a {self.feria}"

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

        return errors

    @classmethod
    def puesto_libre(cls, feria):
        """Retorna el número del primer puesto libre en la feria."""
        puestos_tomados = set(
            feria.inscripcion_set
                .select_for_update()
                .filter(estado="confirmada")
                .values_list("numero_puesto", flat=True)
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
            inscripcion = cls.objects.create(
                emprendedor=emprendedor,
                numero_puesto=cls.puesto_libre(feria) if hay_lugar else None,
                feria=feria,
                registrado_por=registrado_por,
                estado="confirmada" if hay_lugar else "lista_espera",
            )
        return inscripcion, []

    #El método update actualiza el estado de la inscripción. Esto evita que se creen inscripciones aleatorias y luego se les asigne un emprendedor y una feria.
    #Para cambiar el emprendedor o la feria, se debería crear una nueva inscripción y eliminar la anterior, pudiendo perder el lugar en la fila.

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
            if nuevo_estado == "confirmada" and self.estado != "confirmada":
                # Solo confirmar si hay lugar
                if self.feria.tiene_lugar():
                    self.estado = "confirmada"
                    self.numero_puesto = Inscripcion.puesto_libre(self.feria)
                    self.save()
                else:
                    return ["No hay puestos disponibles para confirmar esta inscripción."]
            elif nuevo_estado == "cancelada" and self.estado == "confirmada":
                # Liberar el puesto si se cancela una inscripción confirmada
                self.estado = "cancelada"
                self.save()
                # Intentar confirmar la siguiente inscripción en lista de espera
                siguiente = (
                    Inscripcion.objects
                    .select_for_update()
                    .filter(feria=self.feria, estado="lista_espera")
                    .order_by("fecha_inscripcion")
                    .first()
                )
                if siguiente:
                    siguiente.estado = "confirmada"
                    siguiente.numero_puesto = Inscripcion.puesto_libre(self.feria)
                    siguiente.save()
            else:
                self.estado = nuevo_estado
                self.save()
        return []
