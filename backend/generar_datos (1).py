import mysql.connector
from mysql.connector import Error
from faker import Faker
import random
from datetime import datetime, timedelta
import math

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'SG_Proyectos'
}

# --- CONFIGURACIÓN DE LA GENERACIÓN DE DATOS ---
NUM_CLIENTES = 15
NUM_RESPONSABLES = 12
NUM_PROYECTOS = 25
NUM_TAREAS_POR_PROYECTO = (8, 20)
NUM_COSTOS_POR_PROYECTO = (2, 6)
NUM_REGISTROS_TIEMPO_TOTAL = 600
NUM_INCIDENCIAS_TOTAL = 80
NUM_CAPACITACIONES_TOTAL = 50
NUM_TECNOLOGIAS_POR_PROYECTO = (1, 4)
NUM_EVALUACIONES_CLIENTE = 20
NUM_DEFECTOS_TOTAL = 350

fake = Faker('es_MX')

clientes_ids = []
responsables_ids = []
proyectos_ids = []
tareas_ids = []

def calcular_finanzas_proyecto(presupuesto):
    costo_total = round(random.uniform(presupuesto * 0.75, presupuesto * 1.12), 2)
    diferencia = presupuesto - costo_total
    ganancia = round(max(0, diferencia), 2)
    perdida = round(max(0, -diferencia), 2)
    return costo_total, ganancia, perdida

def generar_clientes(cursor):
    print(f"Generando {NUM_CLIENTES} clientes...")
    sql = "INSERT INTO Clientes (nombre, sector, pais, contacto_nombre, contacto_email) VALUES (%s, %s, %s, %s, %s)"
    sectores = ['Tecnología', 'Financiero', 'Salud', 'Educación', 'Comercio', 'Gobierno']
    for _ in range(NUM_CLIENTES):
        cursor.execute(sql, (fake.company(), random.choice(sectores), 'México', fake.name(), fake.email()))
        clientes_ids.append(cursor.lastrowid)

def generar_responsables(cursor):
    print(f"Generando {NUM_RESPONSABLES} responsables...")
    sql = "INSERT INTO Responsables (nombre, rol, equipo_asignado, correo, telefono) VALUES (%s, %s, %s, %s, %s)"
    roles = ['Project Manager', 'Tech Lead', 'Developer', 'QA', 'Designer']
    for _ in range(NUM_RESPONSABLES):
        cursor.execute(sql, (fake.name(), random.choice(roles), 'Equipo ' + random.choice(['Alpha', 'Beta']), fake.email(), fake.phone_number()))
        responsables_ids.append(cursor.lastrowid)

def generar_proyectos(cursor):
    print(f"Generando {NUM_PROYECTOS} proyectos...")
    sql = """
    INSERT INTO Proyectos (nombre, descripcion, metodologia, fecha_inicio, fecha_fin, 
                           presupuesto, costo_total, ganancia, perdida, horas_invertidas, 
                           progreso, entregables_count, etapas, cronograma, documentacion, 
                           id_cliente, id_responsable, num_tecnologias_emergentes, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    estados = ['Planificación', 'En Progreso', 'En Revisión', 'Completado', 'En Pausa']
    nombres = ['Sistema Nómina', 'App Bancaria', 'E-commerce', 'Portal Web', 'CRM Ventas', 'ERP']
    
    for i in range(NUM_PROYECTOS):
        inicio = fake.date_between(start_date='-12M', end_date='-1M')
        fin = inicio + timedelta(days=random.randint(60, 300))
        presu = round(random.uniform(80000, 1200000), 2)
        costo, ganancia, perdida = calcular_finanzas_proyecto(presu)
        
        cursor.execute(sql, (
            random.choice(nombres) + f" ({i+1})", fake.text(100), 'Scrum', inicio, fin,
            presu, costo, ganancia, perdida, random.randint(200, 4000), 
            random.uniform(0, 100), random.randint(5, 25), 'Etapa Actual', 'Cronograma', 'Docs',
            random.choice(clientes_ids), random.choice(responsables_ids), 
            random.randint(0, 3), random.choice(estados)
        ))
        proyectos_ids.append(cursor.lastrowid)

def generar_tareas(cursor):
    print("Generando tareas...")
    sql = """INSERT INTO Tareas (id_proyecto, titulo, descripcion, estado, prioridad, horas_estimadas, horas_reales, fecha_inicio, fecha_fin) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    for pid in proyectos_ids:
        for _ in range(random.randint(*NUM_TAREAS_POR_PROYECTO)):
            inicio = fake.date_between(start_date='-10M', end_date='today')
            fin = inicio + timedelta(days=random.randint(3, 30))
            cursor.execute(sql, (pid, 'Tarea Generica', 'Desc', 'Pendiente', 'Media', 10, 8, inicio, fin))
            tareas_ids.append(cursor.lastrowid)

def generar_costos(cursor):
    print("Generando costos...")
    sql = "INSERT INTO Costos (id_proyecto, tipo, proveedor, monto, moneda, fecha) VALUES (%s, %s, %s, %s, %s, %s)"
    for pid in proyectos_ids:
        cursor.execute(sql, (pid, 'Otro', 'AWS', 5000, 'MXN', fake.date_between(start_date='-10M', end_date='today')))

def generar_registros_tiempo(cursor):
    print("Generando tiempos...")
    sql = "INSERT INTO Registro_Tiempo (id_responsable, id_tarea, fecha, descripcion, horasTrabajadas) VALUES (%s, %s, %s, %s, %s)"
    for _ in range(NUM_REGISTROS_TIEMPO_TOTAL):
        # CORREGIDO: Usar date_between en lugar de date_today
        fecha_registro = fake.date_between(start_date='-1y', end_date='today')
        cursor.execute(sql, (random.choice(responsables_ids), random.choice(tareas_ids), fecha_registro, 'Trabajo', '04:00:00'))

def generar_incidencias(cursor):
    print("Generando incidencias...")
    sql = "INSERT INTO Incidencias (id_proyecto, id_tarea, id_responsable, severidad, estado, fecha_reporte, notas) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    for _ in range(NUM_INCIDENCIAS_TOTAL):
        # CORREGIDO: Usar date_between
        fecha_incidencia = fake.date_between(start_date='-1y', end_date='today')
        cursor.execute(sql, (random.choice(proyectos_ids), None, random.choice(responsables_ids), 'Media', 'Abierto', fecha_incidencia, 'Nota'))

def generar_defectos(cursor):
    print(f"Generando {NUM_DEFECTOS_TOTAL} defectos distribuidos por etapa...")
    sql = """
    INSERT INTO Defectos (id_proyecto, tipo_defecto, severidad, estado, etapa_deteccion, fecha_deteccion, fecha_correccion)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    tipos = ['Funcional', 'Interfaz', 'Seguridad', 'Rendimiento', 'Datos']
    severidades = ['Cosmético', 'Menor', 'Mayor', 'Crítico']
    estados = ['Abierto', 'Corregido', 'Rechazado']
    
    # Etapas del ciclo de vida del proyecto (usadas como tiempo en modelo Rayleigh)
    etapas_orden = ['Inicio', 'Planificación', 'Ejecución', 'Monitoreo y Control', 'Cierre']
    
    # Pesos Rayleigh: distribución típica de defectos por etapa
    # Más defectos en Ejecución (pico), decreciendo hacia inicio y cierre
    pesos_rayleigh = [0.05, 0.10, 0.45, 0.30, 0.10]

    for _ in range(NUM_DEFECTOS_TOTAL):
        id_proyecto = random.choice(proyectos_ids)
        etapa_seleccionada = random.choices(etapas_orden, weights=pesos_rayleigh, k=1)[0]
        
        fecha_deteccion = fake.date_between(start_date='-10M', end_date='today')
        fecha_correccion = fecha_deteccion + timedelta(days=5) if random.choice([True, False]) else None
        
        data = (
            id_proyecto, random.choice(tipos), random.choice(severidades), 
            random.choice(estados), etapa_seleccionada, fecha_deteccion, fecha_correccion
        )
        cursor.execute(sql, data)

def generar_capacitaciones(cursor):
    print("Generando capacitaciones...")
    sql = "INSERT INTO Capacitaciones (id_responsable, tema, horas, fecha) VALUES (%s, %s, %s, %s)"
    for _ in range(NUM_CAPACITACIONES_TOTAL):
        # CORREGIDO: Usar date_between
        fecha_cap = fake.date_between(start_date='-1y', end_date='today')
        cursor.execute(sql, (random.choice(responsables_ids), 'Curso X', 20, fecha_cap))

def generar_tecnologias_proyecto(cursor):
    print("Generando tecnologías...")
    sql = "INSERT INTO Tecnologias_Proyecto (id_proyecto, tecnologia, es_emergente, version) VALUES (%s, %s, %s, %s)"
    for pid in proyectos_ids:
        cursor.execute(sql, (pid, 'Python', False, '3.9'))

def generar_evaluaciones_cliente(cursor):
    print("Generando evaluaciones...")
    sql = "INSERT INTO Evaluaciones_Cliente (id_proyecto, calificacion, comentarios, fecha) VALUES (%s, %s, %s, %s)"
    for pid in random.sample(proyectos_ids, 10):
        # CORREGIDO: Usar date_between
        fecha_eval = fake.date_between(start_date='-1y', end_date='today')
        cursor.execute(sql, (pid, 4.5, 'Bien', fecha_eval))

def main():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        print("✓ Conexión exitosa.")
        
        # Generar todo
        generar_clientes(cursor)
        generar_responsables(cursor)
        generar_proyectos(cursor)
        generar_tareas(cursor)
        generar_costos(cursor)
        generar_registros_tiempo(cursor)
        generar_incidencias(cursor)
        generar_defectos(cursor) # <-- Ejecuta la versión con etapas numéricas
        generar_capacitaciones(cursor)
        generar_tecnologias_proyecto(cursor)
        generar_evaluaciones_cliente(cursor)

        cnx.commit()
        print("\n✓ ¡Datos generados!")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals(): cnx.close()

if __name__ == "__main__":
    main()