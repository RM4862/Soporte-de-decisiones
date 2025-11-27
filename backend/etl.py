import mysql.connector
from mysql.connector import Error
from datetime import datetime, date, timedelta

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'SG_Proyectos'
}

class ETLProcessor:
    """Clase para procesar el ETL de SG_Proyectos a DSS_Proyectos"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        self.stats = {k: 0 for k in [
            'dim_tiempo', 'dim_cliente', 'dim_responsable', 'dim_proyecto', 'dim_tarea',
            'fact_proyectos', 'fact_tareas', 'fact_tiempo_trabajo', 'fact_costos',
            'fact_defectos', 'fact_incidencias'
        ]}
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("✓ Conexión establecida correctamente\n")
            return True
        except Error as e:
            print(f"✗ Error al conectar: {e}")
            return False
    
    def disconnect(self):
        if self.cursor: self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("\n✓ Conexión cerrada")
    
    def limpiar_dss(self):
        print("Limpiando tablas DSS...")
        try:
            self.cursor.execute("USE DSS_Proyectos")
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            tablas = [
                'Fact_Incidencias', 'Fact_Defectos', 'Fact_Costos', 'Fact_Tiempo_Trabajo',
                'Fact_Tareas', 'Fact_Proyectos', 'Dim_Tarea', 'Dim_Tiempo',
                'Dim_Responsable', 'Dim_Cliente', 'Dim_Proyecto'
            ]
            for tabla in tablas:
                self.cursor.execute(f"TRUNCATE TABLE {tabla}")
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.connection.commit()
            print("✓ Limpieza completada\n")
        except Error as e:
            print(f"✗ Error al limpiar DSS: {e}")
            raise
    
    def extraer_dim_tiempo(self):
        """Genera fechas desde 2022 hasta 2026 para cubrir todo el historial posible"""
        print("Procesando Dim_Tiempo...")
        try:
            self.cursor.execute("USE DSS_Proyectos")
            insert_query = "INSERT INTO Dim_Tiempo (fecha, dia, mes, trimestre, anio) VALUES (%s, %s, %s, %s, %s)"
            
            start_date = date(2022, 1, 1)
            end_date = date(2026, 12, 31)
            delta = end_date - start_date
            
            batch_data = []
            for i in range(delta.days + 1):
                day = start_date + timedelta(days=i)
                batch_data.append((
                    day, day.day, day.month, (day.month - 1) // 3 + 1, day.year
                ))
                
            # Insertar en lotes para velocidad
            for i in range(0, len(batch_data), 1000):
                self.cursor.executemany(insert_query, batch_data[i:i+1000])
                
            self.stats['dim_tiempo'] = len(batch_data)
            self.connection.commit()
            print(f"✓ {self.stats['dim_tiempo']} registros en Dim_Tiempo (2022-2026)\n")
        except Error as e:
            print(f"✗ Error en Dim_Tiempo: {e}")
            raise

    def extraer_dim_cliente(self):
        print("Procesando Dim_Cliente...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            self.cursor.execute("SELECT * FROM Clientes")
            rows = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            query = "INSERT INTO Dim_Cliente VALUES (%s, %s, %s, %s, %s, %s)"
            data = [(r['id_cliente'], r['nombre'], r['sector'], r['pais'], r['contacto_nombre'], r['contacto_email']) for r in rows]
            self.cursor.executemany(query, data)
            
            self.stats['dim_cliente'] = len(data)
            self.connection.commit()
            print(f"✓ {len(data)} clientes cargados.")
        except Error as e: print(f"✗ Error Dim_Cliente: {e}")

    def extraer_dim_responsable(self):
        print("Procesando Dim_Responsable...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            self.cursor.execute("SELECT * FROM Responsables")
            rows = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            query = "INSERT INTO Dim_Responsable VALUES (%s, %s, %s, %s, %s, %s)"
            data = [(r['id_responsable'], r['nombre'], r['rol'], r['equipo_asignado'], r['correo'], r['telefono']) for r in rows]
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.stats['dim_responsable'] = len(data)
            print(f"✓ {len(data)} responsables cargados.")
        except Error as e: print(f"✗ Error Dim_Responsable: {e}")

    def extraer_dim_proyecto(self):
        print("Procesando Dim_Proyecto...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            self.cursor.execute("SELECT id_proyecto, nombre, metodologia, etapas, fecha_inicio, fecha_fin, horas_invertidas, estado FROM Proyectos")
            rows = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            query = "INSERT INTO Dim_Proyecto VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            data = [(r['id_proyecto'], r['nombre'], r['metodologia'], r['etapas'], r['fecha_inicio'], r['fecha_fin'], r['horas_invertidas'], r['estado']) for r in rows]
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.stats['dim_proyecto'] = len(data)
            print(f"✓ {len(data)} proyectos cargados.")
        except Error as e: print(f"✗ Error Dim_Proyecto: {e}")

    def extraer_dim_tarea(self):
        print("Procesando Dim_Tarea...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            self.cursor.execute("SELECT id_tarea, titulo, prioridad, descripcion, estado, fecha_inicio, fecha_fin FROM Tareas")
            rows = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            query = "INSERT INTO Dim_Tarea VALUES (%s, %s, %s, %s, %s, %s, %s)"
            data = [(r['id_tarea'], r['titulo'], r['prioridad'], r['descripcion'], r['estado'], r['fecha_inicio'], r['fecha_fin']) for r in rows]
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.stats['dim_tarea'] = len(data)
            print(f"✓ {len(data)} tareas cargadas.")
        except Error as e: print(f"✗ Error Dim_Tarea: {e}")

    def extraer_fact_proyectos(self):
        print("Procesando Fact_Proyectos...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            query = """
            SELECT p.*, 
                   (p.presupuesto - p.costo_total) as desv_pre,
                   DATEDIFF(p.fecha_fin, p.fecha_inicio) as desv_t,
                   COALESCE(AVG(ec.calificacion), 0) as satisf,
                   CASE WHEN p.entregables_count > 0 THEN p.defectos_detectados / p.entregables_count ELSE 0 END as tasa
            FROM Proyectos p
            LEFT JOIN Evaluaciones_Cliente ec ON p.id_proyecto = ec.id_proyecto
            GROUP BY p.id_proyecto
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            self.cursor.execute("USE DSS_Proyectos")
            insert_query = """
            INSERT INTO Fact_Proyectos (id_proyecto, id_cliente, id_responsable, id_tiempo, presupuesto, costo_total, ganancia, perdida, progreso, entregables_count, horas_invertidas, desviacion_presupuesto, desviacion_tiempo, tasa_defectos, satisfaccion_cliente, roi)
            VALUES (%s, %s, %s, (SELECT id_tiempo FROM Dim_Tiempo WHERE fecha = %s LIMIT 1), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
            """
            
            count = 0
            for r in rows:
                if r['fecha_inicio']:
                    self.cursor.execute(insert_query, (
                        r['id_proyecto'], r['id_cliente'], r['id_responsable'], r['fecha_inicio'],
                        r['presupuesto'], r['costo_total'], r['ganancia'], r['perdida'],
                        r['progreso'], r['entregables_count'], r['horas_invertidas'],
                        r['desv_pre'], r['desv_t'], r['tasa'], r['satisf']
                    ))
                    count += 1
            
            self.connection.commit()
            self.stats['fact_proyectos'] = count
            print(f"✓ {count} hechos de proyectos cargados.")
        except Error as e: print(f"✗ Error Fact_Proyectos: {e}")

    def extraer_fact_defectos(self):
        print("Procesando Fact_Defectos (CRUCIAL)...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            # Extraemos defectos con fechas válidas
            self.cursor.execute("""
                SELECT id_proyecto, DATE(fecha_deteccion) as fecha, tipo_defecto, severidad, estado, etapa_deteccion, 
                       DATEDIFF(COALESCE(fecha_correccion, CURDATE()), fecha_deteccion) as dias
                FROM Defectos WHERE fecha_deteccion IS NOT NULL
            """)
            rows = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            # Usamos subquery para buscar id_tiempo dinámicamente
            query = """
            INSERT INTO Fact_Defectos (id_proyecto, id_tiempo, cantidad, tipo_defecto, severidad, estado_defecto, etapa_deteccion, dias_correccion)
            VALUES (%s, (SELECT id_tiempo FROM Dim_Tiempo WHERE fecha = %s LIMIT 1), 1, %s, %s, %s, %s, %s)
            """
            
            count = 0
            for r in rows:
                self.cursor.execute(query, (r['id_proyecto'], r['fecha'], r['tipo_defecto'], r['severidad'], r['estado'], r['etapa_deteccion'], r['dias']))
                count += 1
                
            self.connection.commit()
            self.stats['fact_defectos'] = count
            print(f"✓ {count} hechos de defectos cargados.")
        except Error as e: print(f"✗ Error Fact_Defectos: {e}")

    # (Omití Fact_Tareas, Tiempo y Costos para brevedad, pero en tu script real déjalos)
    # Aquí te pongo una versión simplificada de ejecutar_etl que llama a lo vital para tu dashboard.

    def ejecutar_etl(self):
        print("\n=== EJECUTANDO ETL ===")
        inicio = datetime.now()
        
        self.limpiar_dss()
        
        # Dimensiones
        self.extraer_dim_tiempo()
        self.extraer_dim_cliente()
        self.extraer_dim_responsable()
        self.extraer_dim_proyecto()
        self.extraer_dim_tarea()
        
        # Hechos (Prioridad Dashboard)
        self.extraer_fact_proyectos()
        self.extraer_fact_defectos()
        # Puedes agregar aquí las llamadas a las otras tablas de hechos si las necesitas
        
        print(f"\n✓ ETL Finalizado en {(datetime.now()-inicio).total_seconds():.2f}s")
        return True

def main():
    etl = ETLProcessor(DB_CONFIG)
    if etl.connect():
        etl.ejecutar_etl()
        etl.disconnect()

if __name__ == "__main__":
    main()