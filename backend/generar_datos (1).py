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

# --- CONFIGURACIÓN DE VOLUMEN (AUMENTADO) ---
NUM_CLIENTES = 50          # Antes 15
NUM_RESPONSABLES = 20      # Antes 12
NUM_PROYECTOS = 200        # Antes 25 (Esto llenará las gráficas)
NUM_TAREAS_POR_PROYECTO = (10, 40)
NUM_COSTOS_POR_PROYECTO = (5, 15)
NUM_REGISTROS_TIEMPO_TOTAL = 3500
NUM_INCIDENCIAS_TOTAL = 300
NUM_CAPACITACIONES_TOTAL = 100
NUM_TECNOLOGIAS_POR_PROYECTO = (2, 6)
NUM_EVALUACIONES_CLIENTE = 150
NUM_DEFECTOS_TOTAL = 1200  # Muchos defectos para la curva Rayleigh

fake = Faker('es_MX')

clientes_ids = []
responsables_ids = []
proyectos_ids = []
tareas_ids = []

# Pesos para simular Pareto (VIPs)
cliente_weights = [] 

def calcular_finanzas_proyecto(presupuesto):
    # Simula desviaciones realistas
    factor = random.triangular(0.8, 1.3, 0.95) # Normalmente se gasta lo presupuestado, a veces más
    costo_total = round(presupuesto * factor, 2)
    diferencia = presupuesto - costo_total
    ganancia = round(max(0, diferencia), 2)
    perdida = round(max(0, -diferencia), 2)
    return costo_total, ganancia, perdida

def generar_clientes(cursor):
    print(f"Generando {NUM_CLIENTES} clientes...")
    sql = "INSERT INTO Clientes (nombre, sector, pais, contacto_nombre, contacto_email) VALUES (%s, %s, %s, %s, %s)"
    sectores = ['Tecnología', 'Financiero', 'Salud', 'Educación', 'Comercio', 'Gobierno', 'Manufactura', 'Logística']
    
    for _ in range(NUM_CLIENTES):
        cursor.execute(sql, (fake.company(), random.choice(sectores), 'México', fake.name(), fake.email()))
        clientes_ids.append(cursor.lastrowid)
        
    # Asignar pesos a los clientes: 20% son VIPs (peso 10), el resto normales (peso 1)
    # Esto hará que las gráficas no sean planas
    global cliente_weights
    for _ in clientes_ids:
        if random.random() < 0.2: # 20% probabilidad de ser VIP
            cliente_weights.append(10)
        else:
            cliente_weights.append(1)

def generar_responsables(cursor):
    print(f"Generando {NUM_RESPONSABLES} responsables...")
    sql = "INSERT INTO Responsables (nombre, rol, equipo_asignado, correo, telefono) VALUES (%s, %s, %s, %s, %s)"
    roles = ['Project Manager', 'Tech Lead', 'Senior Developer', 'QA Lead', 'Architect']
    for _ in range(NUM_RESPONSABLES):
        cursor.execute(sql, (fake.name(), random.choice(roles), 'Equipo ' + random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega']), fake.email(), fake.phone_number()))
        responsables_ids.append(cursor.lastrowid)

def generar_proyectos(cursor):
    print(f"Generando {NUM_PROYECTOS} proyectos (Dist. Pareto)...")
    sql = """
    INSERT INTO Proyectos (nombre, descripcion, metodologia, fecha_inicio, fecha_fin, 
                           presupuesto, costo_total, ganancia, perdida, horas_invertidas, 
                           progreso, entregables_count, etapas, cronograma, documentacion, 
                           id_cliente, id_responsable, num_tecnologias_emergentes, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    estados = ['Planificación', 'En Progreso', 'En Revisión', 'Completado', 'En Pausa', 'Cancelado']
    metodologias = ['Scrum', 'Kanban', 'Waterfall', 'Híbrida', 'SAFe']
    prefijos = ['Sistema', 'Plataforma', 'App', 'Migración', 'API', 'Dashboard', 'Módulo', 'Infraestructura']
    
    for i in range(NUM_PROYECTOS):
        inicio = fake.date_between(start_date='-2y', end_date='today') # Histórico de 2 años
        duracion = random.randint(30, 365)
        fin = inicio + timedelta(days=duracion)
        
        # Presupuesto variado: Muchos pequeños, pocos gigantes (Triangular)
        presu = round(random.triangular(50000, 5000000, 200000), 2)
        costo, ganancia, perdida = calcular_finanzas_proyecto(presu)
        
        # Selección de cliente basada en pesos (Pareto)
        cliente_asignado = random.choices(clientes_ids, weights=cliente_weights, k=1)[0]
        
        nombre_proy = f"{random.choice(prefijos)} {fake.word().capitalize()} ({i+1})"
        
        estado = random.choices(estados, weights=[0.1, 0.3, 0.1, 0.4, 0.05, 0.05], k=1)[0]
        progreso = 100.0 if estado == 'Completado' else random.uniform(0, 99)

        cursor.execute(sql, (
            nombre_proy, fake.text(100), random.choice(metodologias), inicio, fin,
            presu, costo, ganancia, perdida, random.randint(100, 5000), 
            progreso, random.randint(5, 50), 'Etapa Actual', 'Cronograma Link', 'Docs Link',
            cliente_asignado, random.choice(responsables_ids), 
            random.randint(0, 5), estado
        ))
        proyectos_ids.append(cursor.lastrowid)

def generar_tareas(cursor):
    print("Generando tareas masivas...")
    sql = """INSERT INTO Tareas (id_proyecto, titulo, descripcion, estado, prioridad, horas_estimadas, horas_reales, fecha_inicio, fecha_fin) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    for pid in proyectos_ids:
        num_t = random.randint(*NUM_TAREAS_POR_PROYECTO)
        for _ in range(num_t):
            inicio = fake.date_between(start_date='-2y', end_date='today')
            fin = inicio + timedelta(days=random.randint(1, 20))
            estado = random.choice(['Pendiente', 'En progreso', 'Completada'])
            est = random.randint(4, 40)
            real = est * random.uniform(0.8, 1.5) if estado == 'Completada' else 0
            
            cursor.execute(sql, (pid, fake.sentence(nb_words=4), 'Desc', estado, random.choice(['Alta', 'Media', 'Baja']), est, real, inicio, fin))
            tareas_ids.append(cursor.lastrowid)

def generar_costos(cursor):
    print("Generando costos variados...")
    sql = "INSERT INTO Costos (id_proyecto, tipo, proveedor, monto, moneda, fecha) VALUES (%s, %s, %s, %s, %s, %s)"
    proveedores = ['AWS', 'Azure', 'Google', 'Oracle', 'Atlassian', 'Licencia X', 'Consultora Y']
    
    for pid in proyectos_ids:
        for _ in range(random.randint(*NUM_COSTOS_POR_PROYECTO)):
            monto = random.expovariate(1/10000) # Distribución exponencial para montos (muchos pagos chicos, pocos grandes)
            cursor.execute(sql, (pid, random.choice(['Infra', 'Licencia', 'Servicios']), random.choice(proveedores), round(monto, 2), 'MXN', fake.date_between(start_date='-2y', end_date='today')))

def generar_registros_tiempo(cursor):
    print(f"Generando {NUM_REGISTROS_TIEMPO_TOTAL} registros de tiempo...")
    sql = "INSERT INTO Registro_Tiempo (id_responsable, id_tarea, fecha, descripcion, horasTrabajadas) VALUES (%s, %s, %s, %s, %s)"
    for _ in range(NUM_REGISTROS_TIEMPO_TOTAL):
        horas = random.randint(1, 9)
        cursor.execute(sql, (random.choice(responsables_ids), random.choice(tareas_ids), fake.date_between(start_date='-1y', end_date='today'), 'Dev', f'{horas}:00:00'))

def generar_incidencias(cursor):
    print("Generando incidencias...")
    sql = "INSERT INTO Incidencias (id_proyecto, id_tarea, id_responsable, severidad, estado, fecha_reporte, notas) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    for _ in range(NUM_INCIDENCIAS_TOTAL):
        cursor.execute(sql, (random.choice(proyectos_ids), None, random.choice(responsables_ids), random.choice(['Alta', 'Media', 'Baja']), 'Abierto', fake.date_between(start_date='-1y', end_date='today'), 'Nota'))

def generar_defectos(cursor):
    print(f"Generando {NUM_DEFECTOS_TOTAL} defectos (Rayleigh simulado)...")
    sql = """
    INSERT INTO Defectos (id_proyecto, tipo_defecto, severidad, estado, etapa_deteccion, fecha_deteccion, fecha_correccion)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    tipos = ['Funcional', 'Interfaz', 'Seguridad', 'Performance', 'Datos']
    severidades = ['Cosmético', 'Menor', 'Mayor', 'Crítico']
    etapas = ['Etapa 1', 'Etapa 2', 'Etapa 3', 'Etapa 4', 'Etapa 5']
    pesos_etapa = [0.05, 0.15, 0.50, 0.25, 0.05] # Pico en etapa 3

    for _ in range(NUM_DEFECTOS_TOTAL):
        pid = random.choice(proyectos_ids)
        etapa = random.choices(etapas, weights=pesos_etapa, k=1)[0]
        fecha = fake.date_between(start_date='-1y', end_date='today')
        
        # Correlación: Si es crítico, probable etapa tardía
        sev = random.choice(severidades)
        
        data = (pid, random.choice(tipos), sev, random.choice(['Abierto', 'Corregido']), etapa, fecha, None)
        cursor.execute(sql, data)

def generar_tecnologias_proyecto(cursor):
    print("Generando stack tecnológico...")
    sql = "INSERT INTO Tecnologias_Proyecto (id_proyecto, tecnologia, es_emergente, version) VALUES (%s, %s, %s, %s)"
    techs = ['React', 'Angular', 'Vue', 'Node.js', 'Python', 'Java', 'C#', 'Go', 'Docker', 'K8s', 'AWS']
    for pid in proyectos_ids:
        # Algunos proyectos tienen muchas tecnologías, otros pocas
        count = random.randint(*NUM_TECNOLOGIAS_POR_PROYECTO)
        mis_techs = random.sample(techs, min(count, len(techs)))
        for t in mis_techs:
            cursor.execute(sql, (pid, t, random.choice([True, False]), 'v1.0'))

def generar_evaluaciones_cliente(cursor):
    print("Generando feedback clientes...")
    sql = "INSERT INTO Evaluaciones_Cliente (id_proyecto, calificacion, comentarios, fecha) VALUES (%s, %s, %s, %s)"
    # Solo proyectos completados o avanzados
    for pid in proyectos_ids:
        if random.random() > 0.5: # 50% de proyectos tienen evaluación
            calif = round(random.triangular(1, 5, 4), 2) # Tendencia a buena calificación (4)
            cursor.execute(sql, (pid, calif, 'Comentario', fake.date_between(start_date='-1y', end_date='today')))

def main():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        print("✓ Conectado a BD. Iniciando generación MASIVA...")
        
        generar_clientes(cursor)
        generar_responsables(cursor)
        generar_proyectos(cursor)
        generar_tareas(cursor)
        generar_costos(cursor)
        generar_registros_tiempo(cursor)
        generar_incidencias(cursor)
        generar_defectos(cursor)
        generar_tecnologias_proyecto(cursor)
        generar_evaluaciones_cliente(cursor) # Agregué esta llamada que faltaba

        cnx.commit()
        print("\n" + "="*50)
        print("✓ ¡DATOS GENERADOS CORRECTAMENTE!")
        print(f"  • {NUM_PROYECTOS} Proyectos")
        print(f"  • {NUM_CLIENTES} Clientes")
        print(f"  • ~{len(tareas_ids)} Tareas")
        print("="*50)
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals(): cnx.close()

if __name__ == "__main__":
    main()