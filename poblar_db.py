"""
Script para poblar la base de datos con datos de ejemplo.

Uso:
    python manage.py shell < poblar_db.py
"""

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "feriapp.settings")
django.setup()

from django.contrib.auth.models import User
from app.models import Categoria, Feria, Emprendedor, Visitante, Inscripcion, Resenia
from datetime import date

print("Limpiando datos existentes (excepto superusuarios)...")
Resenia.objects.all().delete()
Inscripcion.objects.all().delete()
Emprendedor.objects.all().delete()
Visitante.objects.all().delete()
Feria.objects.all().delete()
Categoria.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

# ---------- CATEGORÍAS ----------
print("Creando categorías...")
cats_data = [
    ("Artesanías",  "Productos hechos a mano: tejidos, cerámica, madera, cuero y más."),
    ("Gastronomía", "Alimentos y bebidas artesanales, conservas, dulces y comidas típicas."),
    ("Indumentaria", "Ropa, accesorios y calzado de diseño independiente."),
    ("Decoración",  "Objetos decorativos para el hogar, plantas y arte."),
    ("Tecnología",  "Gadgets, electrónica, impresión 3D y productos digitales."),
]
categorias = {}
for nombre, desc in cats_data:
    cat, errors = Categoria.new(nombre, desc)
    if errors:
        print(f"  ERROR en categoría '{nombre}': {errors}")
    else:
        categorias[nombre] = cat
        print(f"  ✓ {nombre}")

# ---------- FERIAS ----------
print("Creando ferias...")
ferias_data = [
    # Ferias futuras — para probar inscripciones
    {
        "nombre": "Feria de Primavera 2026",
        "categorias": ["Artesanías", "Decoración"],
        "fecha_inicio": date(2026, 9, 20),
        "fecha_fin": date(2026, 9, 22),
        "ubicacion": "Plaza San Martín, Córdoba",
        "capacidad_puestos": 10,
    },
    {
        "nombre": "Expo Gastronómica del Sur",
        "categorias": ["Gastronomía"],
        "fecha_inicio": date(2026, 10, 5),
        "fecha_fin": date(2026, 10, 7),
        "ubicacion": "Parque Sarmiento, Córdoba",
        "capacidad_puestos": 5,
    },
    {
        "nombre": "Mercado de Diseño Independiente",
        "categorias": ["Indumentaria", "Artesanías"],
        "fecha_inicio": date(2026, 11, 1),
        "fecha_fin": date(2026, 11, 3),
        "ubicacion": "Centro Cultural, Buenos Aires",
        "capacidad_puestos": 8,
    },
    {
        "nombre": "Tech & Makers Córdoba",
        "categorias": ["Tecnología"],
        "fecha_inicio": date(2026, 8, 15),
        "fecha_fin": date(2026, 8, 16),
        "ubicacion": "Campus UNC, Córdoba",
        "capacidad_puestos": 3,
    },
    # Feria pasada — para habilitar reseñas
    {
        "nombre": "Feria de Invierno 2026",
        "categorias": ["Artesanías", "Gastronomía"],
        "fecha_inicio": date(2026, 6, 1),
        "fecha_fin": date(2026, 6, 15),
        "ubicacion": "Patio Olmos, Córdoba",
        "capacidad_puestos": 5,
    },
]
ferias = {}
for data in ferias_data:
    cats = [categorias[c] for c in data["categorias"] if c in categorias]
    feria, errors = Feria.new(
        nombre=data["nombre"],
        categorias=cats,
        fecha_inicio=data["fecha_inicio"],
        fecha_fin=data["fecha_fin"],
        ubicacion=data["ubicacion"],
        capacidad_puestos=data["capacidad_puestos"],
    )
    if errors:
        print(f"  ERROR en feria '{data['nombre']}': {errors}")
    else:
        ferias[data["nombre"]] = feria
        print(f"  ✓ {data['nombre']}")

# ---------- SUPERUSUARIO ----------
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.create_superuser("admin", "admin@feriapp.com", "admin1234")
    print("  ✓ Superusuario creado: admin / admin1234")

# ---------- EMPRENDEDORES ----------
print("Creando emprendedores...")
emprendedores_data = [
    ("emp1", "María",   "González",  "maria@ejemplo.com",   "Artesanías",  "3514001001"),
    ("emp2", "Carlos",  "Romero",    "carlos@ejemplo.com",  "Gastronomía", "3514002002"),
    ("emp3", "Lucía",   "Fernández", "lucia@ejemplo.com",   "Indumentaria","3514003003"),
    ("emp4", "Tomás",   "Pérez",     "tomas@ejemplo.com",   "Tecnología",  "3514004004"),
    ("emp5", "Ana",     "López",     "ana@ejemplo.com",     "Decoración",  "3514005005"),
    ("emp6", "Rodrigo", "Sosa",      "rodrigo@ejemplo.com", "Artesanías",  "3514006006"),
]
emprendedores = {}
for username, nombre, apellido, email, rubro, tel in emprendedores_data:
    user = User.objects.create_user(username=username, password="test1234")
    emp, errors = Emprendedor.new(
        nombre=nombre, apellido=apellido, email=email,
        rubro=rubro, telefono=tel, usuario=user,
    )
    if errors:
        print(f"  ERROR en emprendedor '{nombre}': {errors}")
    else:
        emprendedores[username] = emp
        print(f"  ✓ {apellido}, {nombre} (@{username} / pass: test1234)")

# ---------- VISITANTES ----------
print("Creando visitantes...")
visitantes_data = [
    ("vis1", "Juan",    "Martínez", "juan@ejemplo.com"),
    ("vis2", "Sofía",   "García",   "sofia@ejemplo.com"),
    ("vis3", "Diego",   "Torres",   "diego@ejemplo.com"),
    ("vis4", "Valentina","Ruiz",    "valentina@ejemplo.com"),
]
visitantes = {}
for username, nombre, apellido, email in visitantes_data:
    user = User.objects.create_user(username=username, password="test1234")
    vis, errors = Visitante.new(nombre=nombre, apellido=apellido, email=email, usuario=user)
    if errors:
        print(f"  ERROR en visitante '{nombre}': {errors}")
    else:
        visitantes[username] = vis
        print(f"  ✓ {apellido}, {nombre} (@{username} / pass: test1234)")

# ---------- INSCRIPCIONES (ferias futuras, via new()) ----------
print("Creando inscripciones en ferias futuras...")
inscripciones_futuras = [
    ("emp1", "Feria de Primavera 2026"),
    ("emp2", "Expo Gastronómica del Sur"),
    ("emp3", "Mercado de Diseño Independiente"),
    ("emp4", "Tech & Makers Córdoba"),
    ("emp5", "Feria de Primavera 2026"),
    ("emp6", "Feria de Primavera 2026"),  # entrará en lista de espera si la feria es chica
]
for emp_username, feria_nombre in inscripciones_futuras:
    emp = emprendedores.get(emp_username)
    feria = ferias.get(feria_nombre)
    if not emp or not feria:
        print(f"  SKIP: {emp_username} → {feria_nombre} (no encontrado)")
        continue
    insc, errors = Inscripcion.new(emprendedor=emp, feria=feria, registrado_por=admin_user)
    if errors:
        print(f"  ERROR: {emp_username} → {feria_nombre}: {errors}")
    else:
        print(f"  ✓ {emp.apellido} en '{feria_nombre}' [{insc.estado}]")

# ---------- INSCRIPCIONES (feria pasada, directo a BD) ----------
# Usamos objects.create() porque new() valida que la feria no haya terminado.
# Para datos de seed es correcto saltear esa regla de negocio.
print("Creando inscripciones en feria pasada (Feria de Invierno 2026)...")
feria_invierno = ferias.get("Feria de Invierno 2026")
insc_pasadas = [
    ("emp1", 1), ("emp2", 2), ("emp3", 3), ("emp4", 4),
]
for emp_username, numero_puesto in insc_pasadas:
    emp = emprendedores.get(emp_username)
    if not emp or not feria_invierno:
        continue
    insc = Inscripcion.objects.create(
        emprendedor=emp,
        feria=feria_invierno,
        numero_puesto=numero_puesto,
        registrado_por=admin_user,
        estado='confirmada',
    )
    print(f"  ✓ {emp.apellido} en 'Feria de Invierno 2026' [confirmada, puesto {numero_puesto}]")

# ---------- RESEÑAS ----------
print("Creando reseñas...")
resenias_data = [
    ("vis1", "emp1", "Feria de Invierno 2026", 5, "Excelente atención y productos únicos."),
    ("vis2", "emp2", "Feria de Invierno 2026", 4, "Muy rica la comida, volvería sin dudas."),
    ("vis3", "emp3", "Feria de Invierno 2026", 5, "Ropa increíble, muy buen gusto."),
    ("vis1", "emp4", "Feria de Invierno 2026", 3, "Interesante pero le faltó variedad."),
    ("vis4", "emp2", "Feria de Invierno 2026", 4, "Muy buena propuesta gastronómica."),
    ("vis2", "emp1", "Feria de Invierno 2026", 5, "Los tejidos son increíbles, altísima calidad."),
]
for vis_username, emp_username, feria_nombre, calificacion, comentario in resenias_data:
    vis = visitantes.get(vis_username)
    emp = emprendedores.get(emp_username)
    feria = ferias.get(feria_nombre)
    if not vis or not emp or not feria:
        print(f"  SKIP: {vis_username} → {emp_username} (no encontrado)")
        continue
    resenia, errors = Resenia.new(
        emprendedor=emp, visitante=vis, feria=feria,
        calificacion=calificacion, comentario=comentario,
    )
    if errors:
        print(f"  ERROR: {vis_username} → {emp_username}: {errors}")
    else:
        print(f"  ✓ {vis.apellido} reseñó a {emp.apellido} [{calificacion}⭐]")

print("\n¡Listo! Base de datos poblada.")
print("\nUsuarios creados:")
print("  admin          / admin1234  (superusuario)")
print("  emp1..emp6     / test1234   (emprendedores)")
print("  vis1..vis4     / test1234   (visitantes)")
