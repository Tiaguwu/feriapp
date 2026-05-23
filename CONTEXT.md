# Contexto del proyecto: FeriApp

## ¿Qué es este proyecto?

FeriApp es una aplicación web de gestión de ferias y emprendedores desarrollada con Django 5.1+ y Python 3.13+.
Es un trabajo práctico integrador universitario.
El proyecto está **en construcción**: hay código base ya implementado y partes marcadas con `# TODO` que los estudiantes deben completar.

---

## Stack tecnológico

- Python 3.13+
- Django 5.1+
- SQLite (base de datos de desarrollo)
- Bootstrap 5.3 (frontend, via CDN)
- `django.test.TestCase` (tests unitarios)
- Git + GitHub (control de versiones)

---

## Estructura del proyecto

```
feriapp/
├── feriapp/
│   ├── settings.py        # Configuración Django
│   ├── urls.py            # include("app.urls", namespace="ferias") + admin/
│   └── wsgi.py
├── app/                   # App principal
│   ├── models.py          # Modelos del dominio
│   ├── views.py           # Vistas (FBV)
│   ├── urls.py            # URLs con app_name = "app" e incluidas con namespace "ferias"
│   ├── admin.py           # Registro de modelos en el admin
│   ├── apps.py
│   ├── fixtures/
│   │   └── ferias.json    # 4 instancias de Feria para poblar la BD
│   ├── templates/
│   │   ├── base.html            # Layout base con navbar Bootstrap
│   │   └── ferias/
│   │       ├── home.html        # Panel de inicio con cards vacías (TODO)
│   │       └── lista_ferias.html # Tabla de ferias activas
│   └── tests/
│       ├── test_models.py  # Tests del modelo Feria (validate, new, update)
│       └── __init__.py
├── manage.py
├── requirements.txt       # django>=5.1,<6.0
├── db.sqlite3
├── README.md
├── CONTEXT.md
└── .gitignore
```

---

## Modelo actual implementado: `Feria`

```python
class Feria(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)  # Por ahora CharField, luego será FK a Categoria
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    ubicacion = models.CharField(max_length=200)
    capacidad_puestos = models.PositiveIntegerField()
    activa = models.BooleanField(default=True)

    def __str__(self): ...
    def puestos_ocupados(self) -> int: ...   # cuenta Inscripcion con estado="confirmada"
    def puestos_disponibles(self) -> int: ... # capacidad_puestos - puestos_ocupados()
    def tiene_lugar(self) -> bool: ...        # puestos_disponibles() > 0

    @classmethod
    def validate(cls, nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos) -> list[str]: ...
    @classmethod
    def new(cls, nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos) -> tuple[Feria | None, list[str]]: ...
    def update(self, nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos) -> list[str]: ...
```

**Patrón de validate/new/update**:
- `validate` retorna lista de strings con errores. Lista vacía = datos válidos.
- `new` llama a `validate`, si hay errores retorna `(None, errors)`, si no crea y retorna `(instancia, [])`.
- `update` llama a `validate`, si hay errores retorna la lista sin modificar, si no guarda con `self.save()` y retorna `[]`.

**Validaciones en `validate`**:
- `nombre`, `categoria`, `ubicacion` no pueden estar vacíos
- `capacidad_puestos` debe ser > 0
- `fecha_fin` no puede ser anterior a `fecha_inicio`

---

## Modelos pendientes de implementar (TODO de los estudiantes)

Los estudiantes deben agregar estos modelos en `app/models.py`:

### `Categoria`
- `nombre` (CharField, unique)
- `descripcion` (TextField, blank=True)
- Refactorizar `Feria.categoria` de CharField a FK → Categoria (PROTECT)

### `Emprendedor`
- `nombre`, `apellido` (CharField)
- `email` (CharField, unique)
- `rubro` (CharField)
- `telefono` (CharField, optional)
- `usuario` (OneToOneField → User, CASCADE)

### `Inscripcion`
- `emprendedor` (FK → Emprendedor, CASCADE)
- `feria` (FK → Feria, CASCADE)
- `numero_puesto` (PositiveIntegerField)
- `fecha_inscripcion` (DateField, auto_now_add=True)
- `estado` (CharField, choices: `confirmada` / `lista_espera` / `cancelada`)
- `registrado_por` (FK → User, SET_NULL, null=True)
- Constraint: `UniqueConstraint(fields=["feria", "numero_puesto"], name="puesto_unico_por_feria")`
- Classmethod: `validate`, `new`, `update` (mismo patrón que Feria)

---

## Vistas actuales implementadas

```python
def home(request):         # GET /  → ferias/home.html — contexto vacío (TODO: agregar estadísticas)
def lista_ferias(request): # GET /ferias/ → ferias/lista_ferias.html — contexto: {"ferias": queryset activas}
```

## Vistas pendientes (TODO)

```python
def detalle_feria(request, pk)           # GET /ferias/<pk>/
def nueva_feria(request)                 # GET+POST /ferias/nueva/
def lista_emprendedores(request)         # GET /emprendedores/
def nueva_inscripcion(request)           # GET+POST /inscripciones/nueva/
def cancelar_inscripcion(request, pk)    # POST /inscripciones/<pk>/cancelar/
```

---

## Autenticación

- No hay vistas de login, logout ni registro expuestas en las rutas actuales del proyecto.
- La navegación pública no depende de `user.is_authenticated` ni de templates de `registration/`.
- `django.contrib.auth` sigue instalado porque Django admin lo requiere.
- Si más adelante se agrega autenticación, habrá que definir rutas, templates y comportamiento de acceso de forma explícita.

---

## Admin

`app/admin.py` tiene `admin.site.register(Feria)` básico.
Los estudiantes deben reemplazarlo por `@admin.register` con:
- `list_display`
- `list_filter`
- `search_fields`
- `date_hierarchy` (campo `fecha_inicio` de Feria)

---

## Templates

- `base.html` está en `app/templates/base.html`. Usa `{% block title %}` y `{% block content %}`.
- La navbar actual solo muestra navegación general de la app; no renderiza acciones de autenticación.
- Los templates de la app van en `app/templates/ferias/`.
- Bootstrap 5.3 via CDN (no instalado localmente).
- Para barra de ocupación: `{% widthratio feria.puestos_ocupados feria.capacidad_puestos 100 %}` con `<div class="progress-bar">`.

---

## Tests actuales (pasan ✅)

En `app/tests/test_models.py`:
- `test_str_retorna_nombre`
- `test_activa_por_defecto`
- `test_puestos_disponibles_igual_a_capacidad_sin_inscripciones`
- `test_tiene_lugar_true_con_capacidad_libre`
- `test_validate_datos_correctos_retorna_lista_vacia`
- `test_validate_nombre_vacio_retorna_error`
- `test_validate_fecha_fin_anterior_a_inicio_retorna_error`
- `test_validate_capacidad_cero_retorna_error`
- `test_new_crea_feria_con_datos_validos`
- `test_new_con_datos_invalidos_retorna_errores_y_no_crea`
- `test_update_modifica_datos_correctamente`
- `test_update_con_datos_invalidos_no_modifica`

---

## Consultas ORM pendientes

Actualmente `consultas.py` no existe en el árbol del proyecto. Si se incorpora, estas serían consultas razonables a implementar:

```python
def ferias_activas_por_categoria(nombre_categoria: str) -> QuerySet: ...
def emprendedores_en_feria(feria_id: int) -> QuerySet: ...
def top_n_emprendedores_mas_activos(n: int) -> QuerySet: ...  # usa annotate + order_by
def ferias_sin_lugar() -> QuerySet: ...  # usa annotate + F expression
```

---

## Convenciones del proyecto

- Vistas: FBV (Function-Based Views), no CBV
- URLs: las rutas públicas se referencian con el namespace `ferias`, por ejemplo `{% url 'ferias:home' %}`
- Templates: siempre extienden `base.html`
- Modelos: siempre incluir `__str__`, `validate`, `new`, `update`
- Tests: usar `django.test.TestCase`, no `pytest`
- Commits semánticos: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`

---

## Cómo correr el proyecto

```bash
python -m venv .venv && source .venv/bin/activate  # o .\.venv\Scripts\Activate.ps1 en Windows
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata app/fixtures/ferias.json
python manage.py test -v 2
python manage.py runserver
```

## 📋 Seguimiento Global del Proyecto FeriApp

### 🗄️ 1. Base de Datos y Migraciones
- [x] Migraciones iniciales creadas y commiteadas.
- [ ] Todas las migraciones futuras commiteadas y funcionales.

---

### 📦 2. Modelos (`app/models.py`)
*Patrón obligatorio: todos los modelos deben incluir los métodos `validate()`, `new()` y `update()`.*

- [ ] **Categoria** (nombre, descripcion).
    - [ ] `validate` / `new` / `update` 
    - [ ] **Método de negocio**: `obtener_ferias_activas()` (Retorna las ferias vigentes asociadas a esta categoría).

- [x] **Feria** (nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos, activa).
    - [x] `validate` / `new` / `update` 
    - [ ] **Método de negocio**: `calcular_puestos_disponibles()` (Calcula la capacidad restante restando las inscripciones confirmadas).
    - [ ] **Método de negocio (Opcional 4)**: `clonar_edicion_anterior()` (Clona la información histórica para una nueva edición anual).
    
- [x] **Emprendedor** (nombre, apellido, email, rubro, telefono, usuario).
    - [x] `validate` / `new` / `update` 
    - [ ] **Método de negocio**: `calcular_valoracion_promedio()` (Calcula el puntaje acumulado a partir de las reseñas de visitantes).

- [x] **Visitante** (nombre, apellido, email, usuario, fecha_registro).
    - [x] `validate` / `new` / `update` 
    - [ ] **Método de negocio**: `puede_reseñar_feriante(emprendedor)` (Verifica si el visitante asistió a una feria donde participó el emprendedor antes de permitir escribir la reseña).

- [x] **Inscripcion** (emprendedor, feria, numero_puesto, fecha_inscripcion, estado, registrado_por).
    - [x] `validate` / `new` / `update` 
    - [ ] **Método de negocio**: `cambiar_estado_inscripcion(nuevo_estado)` (Maneja la lógica transicional entre confirmada, lista de espera o cancelada).

- [ ] **Resena** (feriante, visitante, puntaje, comentario, fecha_creacion).
    - [ ] `validate` / `new` / `update` 
    - [ ] **Método de negocio**: `validar_escala_puntaje()` (Valida que la calificación se encuentre estrictamente dentro del rango establecido).

- [ ] **Notificacion** *(Opcional 1)* (usuario, asunto, mensaje, leida, fecha_creacion).
    - [ ] `validate` / `new` / `update` 
    - [ ] **Método de negocio**: `marcar_leida()` (Cambia el estado de visibilidad del mensaje).

- [ ] **Sector** *(Opcional 2)* (edicion, nombre, capacidad_puestos, tiene_conexion_electrica).
    - [ ] `validate` / `new` / `update` 
    - [ ] **Método de negocio**: `verificar_disponibilidad_electrica()` (Determina si el sector cuenta con infraestructura para conexiones activas).

---

### ⚙️ 3. Formularios (`app/forms.py`)
*Requisito: Al menos 2 formularios deben tener validación personalizada.*

- [ ] `RegistroUsuarioForm` (Para el Sign Up de usuarios).
- [ ] `FeriaForm` (Formulario de creación de feria).
- [ ] `InscripcionForm` (Formulario de inscripción a una feria).
- [ ] `ResenaForm` (Para calificar a un emprendedor).
- [ ] `[Validación Personalizada 1]` aplicada.
- [ ] `[Validación Personalizada 2]` aplicada.

---

### 🖥️ 4. Vistas (`app/views.py`)
*Requisito: Únicamente Class Based Views (CBV). Todas protegidas con `@login_required` o `LoginRequiredMixin`.*

- [ ] `HomeView`: Home con estadísticas generales calculadas de la app.
- [ ] `FeriaListView`: Tabla de ferias con filtro por categoría.
- [ ] `FeriaDetailView`: Detalle con info, emprendedores y barra de ocupación.
- [ ] `FeriaCreateView`: Formulario de creación.
- [x] `EmprendedorListView`: Listado general de emprendedores.
- [ ] `PerfilUsuarioView` : Perfil de usuario.
- [ ] `EmprendedorDetailView` : Mustra informacion de los emprendedores.
- [x] `VisitanteListView`: Listado general de visitantes.
- [ ] `InscripcionCreateView`: Solicitar inscripción.
- [ ] `InscripcionListView`: Ver mis inscripciones (para un emprendedor).
- [ ] `InscripcionDeleteView` / Update: Cancelación de inscripciones.
- [ ] `ResenaCreateView`: Dejar una reseña.
- [ ] *(Opcional)* Lógica para clonar ferias (Ediciones).
- [ ] *(Opcional)* Sección de Feriantes Destacados (calculado por reseñas).

---

### 🎨 5. Templates HTML (`app/templates/`)
*Requisito: Bootstrap 5 responsivos. Frontend sin uso de Javascript para lógica compleja.*

- [ ] `base.html` (Navbar dinámica: cambia según autenticación).
- [ ] `home.html` (Renderiza el bloque de estadísticas generales).
- [ ] **Subcarpeta `ferias/`**
    - [ ] `lista_ferias.html` (Tabla responsiva de ferias con barra de filtros por categoría).
    - [ ] `detalle_feria.html` (Muestra el detalle estructurado de la feria y los feriantes asignados).
    - [ ] `formulario_feria.html` (Interfaz limpia de Bootstrap para creación de ferias).
- [x] **Subcarpeta `emprendedores/`**
    - [x] `lista_emprendedores.html` (Tabla Bootstrap con columnas ordenadas y enlaces directos).
    - [x] `detalle_emprendedor.html` (Ficha limpia del perfil de usuario y rubros comerciales).
- [x] **Subcarpeta `visitantes/`**
    - [x] `lista_visitantes.html` (Visualización ordenada de los asistentes al sistema).
- [ ] **Subcarpeta `inscripciones/`**
    - [ ] `formulario_inscripcion.html` (Campos adaptados para postularse a puestos).
    - [ ] `mis_inscripciones.html` (Listado con badges de color según el estado: confirmada/espera/cancelada).
- [ ] **Subcarpeta `resenas/`**
    - [ ] `formulario_resena.html` (Campos estructurados para comentarios y puntajes).
- [x] **Subcarpeta `registration/`** (Ubicada en la raíz de templates)[cite: 31].
    - [ ] `login.html` (Formulario de inicio de sesión estilizado con Bootstrap y libre de CSS inline).
    - [ ] `registro.html` (Interfaz de alta de usuarios comunes).

---

### 🌐 6. Enrutamiento (`app/urls.py` y `feriapp/urls.py`)
- [ ] Ruta de Inicio/home (`/`).
- [ ] Rutas de Autenticación (`accounts/`) conectadas
- [ ] Rutas de Ferias (`/ferias/`, `/ferias/<pk>/`, `/ferias/nueva/`).
- [x] Rutas de Emprendedores (`/emprendedores/`, `/emprendedores/<pk>/`).
- [x] Rutas de Visitantes (`/visitantes/`).
- [ ] Rutas de Inscripciones (`/inscripciones/`, `/inscripciones/nueva/`).
- [ ] Rutas de Reseñas (,`/resenas/``/resenas/nueva/`).

---

### 🔐 7. Autenticación y Permisos
- [ ] Login funcionando.
- [ ] Logout funcionando.
- [ ] Registro (Sign up) funcionando.
- [ ] Permisos configurables según tipo de usuario (Admin/Organización, Emprendedor, Visitante).

---

### 🛡️ 8. Panel de Administración (`app/admin.py`)
*Requisito: Usar el default de Django con modelos configurados y personalizados.*
- [x] `FeriaAdmin` (`list_display`, `list_filter` u otras personalizaciones).
- [x] `EmprendedorAdmin`.
- [x] `VisitanteAdmin`.
- [ ] `CategoriaAdmin`.
- [ ] `InscripcionAdmin`.
- [ ] `ResenaAdmin`.
- [ ] `NotificacionAdmin`
- [ ] `SectorAdmin`


---

### 🧪 9. Tests Unitarios (`app/tests.py`)
*Requisito: Todos los modelos testeados y con tests pasando.*
- [ ] Tests de `Feria` (`validate`, `new`, `update`).
    - [ ] `test_metodo_puestos_disponibles`
- [x] Tests de `Emprendedor` (`validate`, `new`, `update`).
    - [ ] `test_metodo_valoracion_promedio`
- [x] Tests de `Visitante` (`validate`, `new`, `update`).
    - [ ] `test_metodo_puede_reseñar`
- [ ] Tests de `Categoria` (`validate`, `new`, `update`).
    - [ ] `test_metodo_ferias_activas`
- [ ] Tests de `Inscripcion` (`validate`, `new`, `update`).
    - [ ] `test_metodo_cambio_estado`
- [ ] Tests de `Resena` (`validate`, `new`, `update`).
    - [ ] `test_metodo_escala_puntaje`

---

### 📦 10. Archivos Estáticos y Datos de Carga (`app/fixtures/`)
*Estrategia grupal para estandarizar el desarrollo y asegurar uniformidad en las pruebas internas.*

- [ ] **Crear el archivo base `app/fixtures/initial_data.json`** conteniendo los registros semilla idénticos para todo el equipo:
    - [ ] Usuarios del sistema preconfigurados (Admin, Staff, Cuentas de prueba).
    - [ ] Mínimo 3 instancias completas de la clase `Categoria`.
    - [ ] Mínimo 3 instancias completas de la clase `Feria` distribuidas por fechas.
    - [ ] Mínimo 3 instancias completas de la clase `Emprendedor` vinculadas a sus usuarios.
    - [ ] Mínimo 3 instancias completas de la clase `Visitante` vinculadas a sus usuarios.
- [ ] **Documentar el comando de carga** en el archivo principal de lectura para el equipo: `python manage.py loaddata initial_data`.

---

### 📝 11. Documentación y Control de Versiones
- [x] Repositorio forkeado correctamente.
- [ ] `README.md` actualizado con documentación del proyecto.
- [ ] Entrega por mail con formato exacto: `"GRUPO X - [Tipo de proyecto] - Entrega N° X"`.