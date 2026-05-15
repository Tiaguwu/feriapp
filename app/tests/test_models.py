"""Tests de comportamiento para el modelo Feria."""

from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import User

from app.models import Emprendedor
from app.models import Feria
from app.models import Visitante

class FeriaModelTest(TestCase):
    """Verifica validaciones y operaciones básicas del modelo Feria."""

    def setUp(self):
        """Crea una feria base reutilizable para cada caso de prueba."""
        self.feria = Feria.objects.create(
            nombre="Feria de Invierno",
            categoria="Artesanías",
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=date(2026, 7, 3),
            ubicacion="Plaza Central",
            capacidad_puestos=10,
        )

    # --- __str__ y métodos simples ---

    def test_str_retorna_nombre(self):
        self.assertEqual(str(self.feria), "Feria de Invierno")

    def test_activa_por_defecto(self):
        self.assertTrue(self.feria.activa)

    def test_puestos_disponibles_igual_a_capacidad_sin_inscripciones(self):
        self.assertEqual(self.feria.puestos_disponibles(), 10)

    def test_tiene_lugar_true_con_capacidad_libre(self):
        self.assertTrue(self.feria.tiene_lugar())

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = Feria.validate(
            "Tech Patagonia",
            "Tecnología",
            date(2026, 9, 1),
            date(2026, 9, 3),
            "Centro Cultural",
            20,
        )
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = Feria.validate(
            "",
            "Tecnología",
            date(2026, 9, 1),
            date(2026, 9, 3),
            "Centro Cultural",
            20,
        )
        self.assertTrue(len(errors) > 0)

    def test_validate_fecha_fin_anterior_a_inicio_retorna_error(self):
        errors = Feria.validate(
            "Feria",
            "Categoría",
            date(2026, 9, 10),
            date(2026, 9, 5),  # fin < inicio
            "Ubicación",
            10,
        )
        self.assertTrue(len(errors) > 0)

    def test_validate_capacidad_cero_retorna_error(self):
        errors = Feria.validate(
            "Feria",
            "Categoría",
            date(2026, 9, 1),
            date(2026, 9, 3),
            "Ubicación",
            0,
        )
        self.assertTrue(len(errors) > 0)

    # --- new ---

    def test_new_crea_feria_con_datos_validos(self):
        feria, errors = Feria.new(
            "Mercado de Diseño",
            "Artesanías",
            date(2026, 8, 1),
            date(2026, 8, 3),
            "Muelle Turístico",
            15,
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(feria)
        self.assertEqual(feria.nombre, "Mercado de Diseño")
        self.assertTrue(Feria.objects.filter(nombre="Mercado de Diseño").exists())

    def test_new_con_datos_invalidos_retorna_errores_y_no_crea(self):
        count_antes = Feria.objects.count()
        feria, errors = Feria.new("", "", None, None, "", 0)
        self.assertIsNone(feria)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Feria.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.feria.update(
            "Feria de Invierno",
            "Artesanías",
            date(2026, 7, 1),
            date(2026, 7, 3),
            "Parque Central",
            20,
        )
        self.assertEqual(errors, [])
        self.feria.refresh_from_db()
        self.assertEqual(self.feria.ubicacion, "Parque Central")
        self.assertEqual(self.feria.capacidad_puestos, 20)

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.feria.update("", "", None, None, "", 0)
        self.assertTrue(len(errors) > 0)
        self.feria.refresh_from_db()
        self.assertEqual(self.feria.nombre, "Feria de Invierno")  # sin cambios

class EmprendedorModelTest(TestCase):

    def setUp(self):
        # Creamos un usuario de base para las pruebas de OneToOneField
        self.user = User.objects.create_user(username='tiago_user', password='password123')
        self.emprendedor = Emprendedor.objects.create(
            nombre="Tiago",
            apellido="Caranchi",
            email="tiago@ejemplo.com",
            rubro="Artesanias",
            telefono="2901522196",
            usuario=self.user
        )

    # --- __str__ y metadatos ---

    def test_str_retorna_apellido_nombre(self):
        # Verifica que el método __str__ use f-strings con el formato correcto
        self.assertEqual(str(self.emprendedor), "Caranchi Tiago")

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacio(self):
        # Verifica que con todos los campos correctos no haya errores
        errors = Emprendedor.validate(
            self.emprendedor.nombre, 
            self.emprendedor.apellido, 
            self.emprendedor.email, 
            self.emprendedor.rubro, 
            self.emprendedor.telefono, 
            self.emprendedor.usuario
        )
        self.assertEqual(errors, [])

    def test_validate_campos_vacios(self):

        errors = Emprendedor.validate(
            "", "  ", " ", "Rubro", "123", self.user
        )
        self.assertIn("El nombre es obligatorio.", errors)
        self.assertIn("El apellido es obligatorio.", errors)
        self.assertIn("El email es obligatorio.", errors)

    def test_validate_sin_usuario_retorna_error(self):

        errors = Emprendedor.validate(
            "Tiago", "C", "t@t.com", "Rubro", "123", None
        )
        self.assertIn("El usuario asociado es obligatorio.", errors)

    # --- new ---

    def test_new_con_datos_validos(self):

        user2 = User.objects.create_user(username='user2', password='123')
        instacia, errors = Emprendedor.new(
            "Nuevo", "Feriante", "nuevo@test.com", "Textil", "4444", user2
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(instacia)
        self.assertEqual(instacia.nombre, "Nuevo")
        self.assertTrue(Emprendedor.objects.filter(email="nuevo@test.com").exists())

    def test_new_con_datos_invalidos(self):
        count_antes = Emprendedor.objects.count()
        instancia, errors = Emprendedor.new("", "", "", "", "", None)
        self.assertIsNone(instancia)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Emprendedor.objects.count(), count_antes)
    
    # --- update ---

    def test_update_modifica_datos_correctamente(self):

        errors = self.emprendedor.update(
            "Tiago Editado",
            "Caranchi",
            "TiagoC@ejemplo,com",
            "Muebles",
            "2901000000"
        )
        self.assertEqual(errors, [])
        self.emprendedor.refresh_from_db()
        self.assertEqual(self.emprendedor.nombre, "Tiago Editado")

    def test_update_con_datos_invalidos_mantiene_datos_originales(self):

        errors = self.emprendedor.update("","","error@ejemplo.com","","")
        self.assertTrue(len(errors)>0)
        self.emprendedor.refresh_from_db()
        self.assertEqual(self.emprendedor.nombre, "Tiago")

class VisitanteModelTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username='tiago_user', password='password123')
        self.visitante = Visitante.objects.create(
            nombre="Tiago",
            apellido="Caranchi",
            email="tiago@ejemplo.com",
            usuario=self.user
        )

    # --- __str__ y metadatos ---

    def test_str_retorna_apellido_nombre(self):
        self.assertEqual(str(self.visitante), "Caranchi Tiago")

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):

        errors = Visitante.validate(
            self.visitante.nombre,
            self.visitante.apellido,
            self.visitante.email,
            self.visitante.usuario
        )
        self.assertEqual(errors, [])

    def test_validate_campos_vacios(self):

        errors = Visitante.validate(
            "", "", "", self.user
        )

        self.assertIn("El nombre es obligatorio.", errors)
        self.assertIn("El apellido es obligatorio.", errors)
        self.assertIn("El email es obligatorio.", errors)

    def test_validate_sin_usuario_retorna_error(self):
        errors = Visitante.validate(
            "Tiago", "C", "t@t.com", None
        )
        self.assertIn("El usuario asociado es obligatorio.", errors)

    
    # --- new ---

    def test_new_con_datos_validos(self):

        user2 = User.objects.create_user(username='user2', password='123')
        instancia, errors = Visitante.new(
            "Nuevo", "Visitante", "nuevo@test.com", user2
        )

        self.assertEqual(errors, [])
        self.assertIsNotNone(instancia)
        self.assertEqual(instancia.nombre, "Nuevo")
        self.assertTrue(Visitante.objects.filter(email="nuevo@test.com").exists())

    def test_new_con_datos_invalidos(self):
        count_antes = Visitante.objects.count()
        instancia, errors = Visitante.new("", "", "", None)
        self.assertIsNone(instancia)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Visitante.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):

        errors = self.visitante.update(
            "Tiago Editado",
            "Caranchi",
            "TiagoC@ejemplo.com"
        )
        self.assertEqual(errors, [])
        self.visitante.refresh_from_db()
        self.assertEqual(self.visitante.nombre, "Tiago Editado")

    def test_update_con_datos_invalidos_matiene_datos(self):
        
        errors = self.visitante.update("", "", "error@ejemplo.com")
        self.assertTrue(len(errors)>0)
        self.visitante.refresh_from_db()
        self.assertEqual(self.visitante.nombre, "Tiago")
    # def test_tiene_lugar_false_cuando_llena(self): ...
    # def test_puestos_ocupados_cuenta_solo_confirmadas(self): ...
