"""Tests de comportamiento para el modelo Feria."""

from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import User

from app.models import Emprendedor
from app.models import Feria
from app.models import Visitante
from app.models import Inscripcion
from app.models import Categoria

class FeriaModelTest(TestCase):
    """Verifica validaciones y operaciones básicas del modelo Feria."""

    def setUp(self):
        """Crea una feria base reutilizable para cada caso de prueba."""
        # Crear una categoría primero
        self.categoria = Categoria.objects.create(
            nombre="Artesanías",
            descripcion="Ferias de artesanos"
        )
    
        # Crear la feria SIN el campo categoria
        self.feria = Feria.objects.create(
            nombre="Feria de Invierno",
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=date(2026, 7, 3),
            ubicacion="Plaza Central",
            capacidad_puestos=10,
        )
    
        # Asignar la categoría a la feria
        self.feria.categorias.add(self.categoria)

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
        """Verifica que new() crea una feria con datos válidos."""
        # Usar la categoría que ya existe en self.categoria (creada en setUp)
        feria, errors = Feria.new(
            "Mercado de Diseño",
            self.categoria,  # ← Usar la categoría existente, no crear una nueva
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
            self.categoria,
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

class InscripcionModelTest(TestCase):
    """Verifica validaciones y operaciones básicas del modelo Inscripcion."""

    def setUp(self):
        '''Crea una feria base y un emprendedor para cada caso de prueba.'''
        # Usuario emprendedor
        self.user_emp = User.objects.create_user(username='emp_user', password='123')
        self.emprendedor = Emprendedor.objects.create(
            nombre="Andrés", apellido="Rühle", email="andres@ejemplo.com",
            rubro="Textil", telefono="2901497199", usuario=self.user_emp
        )
        # Usuario que registra la inscripción
        self.user_admin = User.objects.create_user(username='admin_user', password='123')
        
        # Crear una categoría primero
        self.categoria = Categoria.objects.create(
            nombre="Artesanías",
            descripcion="Ferias de artesanos"
        )
    
        # Crear la feria SIN el campo categoria
        self.feria = Feria.objects.create(
            nombre="Feria de Invierno",
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=date(2026, 7, 3),
            ubicacion="Plaza Central",
            capacidad_puestos=2
        )
    
        # Asignar la categoría a la feria
        self.feria.categorias.add(self.categoria)
    
        # Crear la inscripción base (después de tener la feria)
        self.inscripcion = Inscripcion.objects.create(
            emprendedor=self.emprendedor,
            feria=self.feria,
            numero_puesto=1,
            registrado_por=self.user_admin,
            estado="confirmada"
        )
    
        # usuarios extra para tests
        self.user2 = User.objects.create_user(username='emp2', password='123')
        self.emp2 = Emprendedor.objects.create(
            nombre="Ana", apellido="Paz", email="ana@ejemplo.com",
            rubro="Joyeria", telefono="2901445566", usuario=self.user2
        )
        self.user3 = User.objects.create_user(username='emp3', password='123')
        self.emp3 = Emprendedor.objects.create(
            nombre="Leo", apellido="Gil", email="leo@ejemplo.com",
            rubro="Carpintería", telefono="2901554433", usuario=self.user3
        )

    # --- __str__ ---

    def test_str_retorna_descripcion_completa(self):
        self.assertEqual(
            str(self.inscripcion),
            "Inscripción de Rühle Andrés a Feria de Invierno. Puesto: 1 - Estado: confirmada"
        )

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = Inscripcion.validate(
            self.emprendedor,
            self.feria,
            self.user_admin
        )
        self.assertEqual(errors, [])

    def test_validate_sin_emprendedor_retorna_error(self):
        errors = Inscripcion.validate(
            None,
            self.feria,
            self.user_admin
        )
        self.assertIn("Debe seleccionar un emprendedor.", errors)
    
    def test_validate_sin_feria_retorna_error(self):
        errors = Inscripcion.validate(
            self.emprendedor,
            None,
            self.user_admin
        )
        self.assertIn("Debe seleccionar una feria.", errors)
    
    def test_validate_sin_usuario_retorna_error(self):
        errors = Inscripcion.validate(
            self.emprendedor,
            self.feria,
            None
        )
        self.assertIn("Debe haber un usuario registrado que realice la inscripción.", errors)
    
    def test_validate_feria_inactiva_retorna_error(self):
        self.feria.activa = False
        self.feria.save()
        errors = Inscripcion.validate(
            self.emprendedor,
            self.feria,
            self.user_admin
        )
        self.assertIn("La feria no está activa.", errors)

    def test_validate_feria_finalizada_retorna_error(self):
        self.feria.fecha_fin = date(1982, 10, 31)
        self.feria.save()
        errors = Inscripcion.validate(
            self.emprendedor,
            self.feria,
            self.user_admin
        )
        self.assertIn("La feria ya terminó.", errors)

    # --- new ---

    def test_new_con_lugar_crea_inscripcion_confirmada(self):

        inscripcion, errors = Inscripcion.new(self.emp2, self.feria, self.user_admin)
        self.assertEqual(errors, [])
        self.assertIsNotNone(inscripcion)
        self.assertEqual(inscripcion.estado, "confirmada")
        self.assertEqual(inscripcion.numero_puesto, 2)

    def test_new_feria_llena_crea_en_lista_espera(self):
        # lleno primero el puesto 2 (último libre)
        Inscripcion.new(self.emp2, self.feria, self.user_admin)

        # creo una inscripción que debería ir a lista de espera
        inscripcion, errors = Inscripcion.new(self.emp3, self.feria, self.user_admin)
        self.assertEqual(errors, [])
        self.assertIsNotNone(inscripcion)
        self.assertEqual(inscripcion.estado, "lista_espera")
        self.assertIsNone(inscripcion.numero_puesto)

    def test_new_con_datos_invalidos_no_crea(self):
        # cuento las inscripciones
        count_antes = Inscripcion.objects.count()

        inscripcion, errors = Inscripcion.new(None, None, None)
        self.assertIsNone(inscripcion)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Inscripcion.objects.count(), count_antes)

    # --- update ---

    def test_update_estado_invalido_retorna_error(self):
        errors = self.inscripcion.update("inexistente")
        self.assertTrue(len(errors) > 0)

    def test_update_cancelar_cambia_estado(self):
        errors = self.inscripcion.update("cancelada")
        self.assertEqual(errors, [])
        self.inscripcion.refresh_from_db()
        self.assertEqual(self.inscripcion.estado, "cancelada")

    def test_update_cancelar_conserva_numero_puesto(self):
        self.inscripcion.update("cancelada")
        self.inscripcion.refresh_from_db()
        self.assertEqual(self.inscripcion.numero_puesto, 1)

    def test_update_cancelar_promueve_lista_espera(self):

        #lleno la lista
        Inscripcion.new(self.emp2, self.feria, self.user_admin)
        # anotar uno que queda en lista de espera
        en_espera, _ = Inscripcion.new(self.emp3, self.feria, self.user_admin)

        # cancelar la inscripcion 1
        self.inscripcion.update("cancelada")

        # el de lista de espera debe haber confirmado y conseguido el numero de puesto del cancelado (1)
        en_espera.refresh_from_db()
        self.assertEqual(en_espera.estado, "confirmada")
        self.assertIsNotNone(en_espera.numero_puesto)
        self.assertEqual(en_espera.numero_puesto, 1)

class CategoriaModelTest(TestCase):
    """Verifica validaciones y operaciones básicas del modelo Categoria."""

    def setUp(self):
        """Crea una categoría base reutilizable para cada caso de prueba."""
        self.categoria = Categoria.objects.create(
            nombre="Tecnología",
            descripcion="Ferias relacionadas con tecnología e innovación",
        )

    # --- __str__ y metadatos ---

    def test_str_retorna_nombre(self):
        """Verifica que el método __str__ devuelve el nombre de la categoría."""
        self.assertEqual(str(self.categoria), "Tecnología")

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        """Verifica que con datos válidos no haya errores."""
        errors = Categoria.validate(
            "Artesanía",
            "Ferias de artesanos y manualidades"
        )
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        """Verifica que el nombre vacío genera un error."""
        errors = Categoria.validate(
            "",
            "Descripción válida"
        )
        self.assertIn("El nombre de la categoría es obligatorio.", errors)

    def test_validate_descripcion_vacia_retorna_error(self):
        """Verifica que la descripción vacía genera un error."""
        errors = Categoria.validate(
            "Gastronomía",
            ""
        )
        self.assertIn("La descripción de la categoría es obligatoria.", errors)

    def test_validate_nombre_solo_espacios_retorna_error(self):
        """Verifica que el nombre con solo espacios genera error."""
        errors = Categoria.validate(
            "   ",
            "Descripción válida"
        )
        self.assertIn("El nombre de la categoría es obligatorio.", errors)

    def test_validate_descripcion_solo_espacios_retorna_error(self):
        """Verifica que la descripción con solo espacios genera error."""
        errors = Categoria.validate(
            "Moda",
            "   "
        )
        self.assertIn("La descripción de la categoría es obligatoria.", errors)

    # --- new ---

    def test_new_crea_categoria_con_datos_validos(self):
        """Verifica que new() crea una categoría con datos válidos."""
        categoria, errors = Categoria.new(
            "Artesanía",
            "Ferias de artesanos y productos hechos a mano"
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(categoria)
        self.assertEqual(categoria.nombre, "Artesanía")
        self.assertTrue(Categoria.objects.filter(nombre="Artesanía").exists())

    def test_new_con_datos_invalidos_retorna_errores_y_no_crea(self):
        """Verifica que new() no crea categoría si los datos son inválidos."""
        count_antes = Categoria.objects.count()
        categoria, errors = Categoria.new("", "")
        self.assertIsNone(categoria)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Categoria.objects.count(), count_antes)

    def test_new_con_nombre_duplicado_deberia_permitir_segun_validate(self):
        categoria1, _ = Categoria.new("Duplicada", "Descripción 1")
        
        # Intentar crear otra con el mismo nombre
        # Esto debería fallar a nivel de BD
        with self.assertRaises(Exception):
            Categoria.objects.create(nombre="Duplicada", descripcion="Descripción 2")

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        """Verifica que update() modifica una categoría existente."""
        errors = self.categoria.update(
            "Tecnología e Innovación",
            "Ferias de tecnología, software e innovación digital"
        )
        self.assertEqual(errors, [])
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, "Tecnología e Innovación")
        self.assertEqual(self.categoria.descripcion, "Ferias de tecnología, software e innovación digital")

    def test_update_con_datos_invalidos_no_modifica(self):
        """Verifica que update() no modifica si los datos son inválidos."""
        nombre_original = self.categoria.nombre
        descripcion_original = self.categoria.descripcion
        
        errors = self.categoria.update("", "")
        
        self.assertTrue(len(errors) > 0)
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, nombre_original)
        self.assertEqual(self.categoria.descripcion, descripcion_original)

    def test_update_con_nombre_vacio_retorna_error_y_no_modifica(self):
        """Verifica que update() con nombre vacío retorna error."""
        descripcion_original = self.categoria.descripcion
        
        errors = self.categoria.update("", "Nueva descripción")
        
        self.assertIn("El nombre de la categoría es obligatorio.", errors)
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, "Tecnología")
        self.assertEqual(self.categoria.descripcion, descripcion_original)

