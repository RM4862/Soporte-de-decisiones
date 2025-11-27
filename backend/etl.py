import mysql.connector
from mysql.connector import Error
from datetime import datetime

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'SG_Proyectos'  # Conectamos primero a SG
}

class ETLProcessor:
    """Clase para procesar el ETL de SG_Proyectos a DSS_Proyectos"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        self.stats = {
            'dim_tiempo': 0,
            'dim_cliente': 0,
            'dim_responsable': 0,
            'dim_proyecto': 0,
            'dim_tarea': 0,
            'fact_proyectos': 0,
            'fact_tareas': 0,
            'fact_tiempo_trabajo': 0,
            'fact_costos': 0,
            'fact_defectos': 0,
            'fact_incidencias': 0
        }
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("✓ Conexión establecida correctamente\n")
            return True
        except Error as e:
            print(f"✗ Error al conectar: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("\n✓ Conexión cerrada")
    
    def limpiar_dss(self):
        """Limpiar las tablas del DSS antes de cargar"""
        print("Limpiando tablas DSS...")
        try:
            self.cursor.execute("USE DSS_Proyectos")
            
            # Desactivar verificación de claves foráneas
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            tablas = [
                'Fact_Incidencias',
                'Fact_Defectos',
                'Fact_Costos',
                'Fact_Tiempo_Trabajo',
                'Fact_Tareas',
                'Fact_Proyectos',
                'Dim_Tarea',
                'Dim_Tiempo',
                'Dim_Responsable',
                'Dim_Cliente',
                'Dim_Proyecto'
            ]
            
            for tabla in tablas:
                self.cursor.execute(f"TRUNCATE TABLE {tabla}")
                print(f"  • {tabla} limpiada")
            
            # Reactivar verificación de claves foráneas
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.connection.commit()
            print("✓ Limpieza completada\n")
            
        except Error as e:
            print(f"✗ Error al limpiar DSS: {e}")
            self.connection.rollback()
            raise
    
    def extraer_dim_tiempo(self):
        """Extraer y cargar dimensión tiempo"""
        print("Procesando Dim_Tiempo...")
        try:
            # Extraer fechas únicas de múltiples tablas en SG
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT DISTINCT fecha_inicio AS fecha FROM Proyectos WHERE fecha_inicio IS NOT NULL
            UNION
            SELECT DISTINCT fecha_fin FROM Proyectos WHERE fecha_fin IS NOT NULL
            UNION
            SELECT DISTINCT fecha_inicio FROM Tareas WHERE fecha_inicio IS NOT NULL
            UNION
            SELECT DISTINCT fecha_fin FROM Tareas WHERE fecha_fin IS NOT NULL
            UNION
            SELECT DISTINCT fecha FROM Registro_Tiempo WHERE fecha IS NOT NULL
            UNION
            SELECT DISTINCT fecha FROM Costos WHERE fecha IS NOT NULL
            UNION
            SELECT DISTINCT fecha_reporte FROM Incidencias WHERE fecha_reporte IS NOT NULL
            UNION
            SELECT DISTINCT fecha_resolucion FROM Incidencias WHERE fecha_resolucion IS NOT NULL
            UNION
            SELECT DISTINCT fecha FROM Capacitaciones WHERE fecha IS NOT NULL
            UNION
            SELECT DISTINCT fecha FROM Evaluaciones_Cliente WHERE fecha IS NOT NULL
            ORDER BY fecha
            """
            
            self.cursor.execute(query)
            fechas = self.cursor.fetchall()
            
            # Cargar en DSS
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Dim_Tiempo (fecha, dia, mes, trimestre, anio)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for row in fechas:
                fecha = row['fecha']
                data = (
                    fecha,
                    fecha.day,
                    fecha.month,
                    (fecha.month - 1) // 3 + 1,  # Calcular trimestre
                    fecha.year
                )
                self.cursor.execute(insert_query, data)
                self.stats['dim_tiempo'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['dim_tiempo']} registros en Dim_Tiempo\n")
            
        except Error as e:
            print(f"✗ Error en Dim_Tiempo: {e}")
            self.connection.rollback()
            raise
    
    def extraer_dim_cliente(self):
        """Extraer y cargar dimensión cliente"""
        print("Procesando Dim_Cliente...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT id_cliente, nombre, sector, pais, contacto_nombre, contacto_email
            FROM Clientes
            """
            
            self.cursor.execute(query)
            clientes = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Dim_Cliente (id_cliente, nombre, sector, pais, contacto_nombre, contacto_email)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            for cliente in clientes:
                data = (
                    cliente['id_cliente'],
                    cliente['nombre'],
                    cliente['sector'],
                    cliente['pais'],
                    cliente['contacto_nombre'],
                    cliente['contacto_email']
                )
                self.cursor.execute(insert_query, data)
                self.stats['dim_cliente'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['dim_cliente']} registros en Dim_Cliente\n")
            
        except Error as e:
            print(f"✗ Error en Dim_Cliente: {e}")
            self.connection.rollback()
            raise
    
    def extraer_dim_responsable(self):
        """Extraer y cargar dimensión responsable"""
        print("Procesando Dim_Responsable...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT 
                id_responsable,
                nombre,
                rol,
                equipo_asignado,
                correo,
                telefono
            FROM Responsables
            """
            
            self.cursor.execute(query)
            responsables = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Dim_Responsable (id_responsable, nombre, rol, equipo_asignado, 
                                        correo, telefono)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            for resp in responsables:
                data = (
                    resp['id_responsable'],
                    resp['nombre'],
                    resp['rol'],
                    resp['equipo_asignado'],
                    resp['correo'],
                    resp['telefono']
                )
                self.cursor.execute(insert_query, data)
                self.stats['dim_responsable'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['dim_responsable']} registros en Dim_Responsable\n")
            
        except Error as e:
            print(f"✗ Error en Dim_Responsable: {e}")
            self.connection.rollback()
            raise
    
    def extraer_dim_proyecto(self):
        """Extraer y cargar dimensión proyecto"""
        print("Procesando Dim_Proyecto...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT 
                id_proyecto,
                nombre,
                metodologia,
                etapas,
                fecha_inicio,
                fecha_fin,
                horas_invertidas,
                estado
            FROM Proyectos
            """
            
            self.cursor.execute(query)
            proyectos = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Dim_Proyecto (id_proyecto, nombre, metodologia, etapas,
                                     fecha_inicio, fecha_fin, horas_invertidas, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for proy in proyectos:
                data = (
                    proy['id_proyecto'],
                    proy['nombre'],
                    proy['metodologia'],
                    proy['etapas'],
                    proy['fecha_inicio'],
                    proy['fecha_fin'],
                    proy['horas_invertidas'],
                    proy['estado']
                )
                self.cursor.execute(insert_query, data)
                self.stats['dim_proyecto'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['dim_proyecto']} registros en Dim_Proyecto\n")
            
        except Error as e:
            print(f"✗ Error en Dim_Proyecto: {e}")
            self.connection.rollback()
            raise
    
    def extraer_dim_tarea(self):
        """Extraer y cargar dimensión tarea"""
        print("Procesando Dim_Tarea...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT 
                id_tarea,
                titulo,
                prioridad,
                descripcion,
                estado,
                fecha_inicio,
                fecha_fin
            FROM Tareas
            """
            
            self.cursor.execute(query)
            tareas = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Dim_Tarea (id_tarea, titulo, prioridad, descripcion, 
                                  estado, fecha_inicio, fecha_fin)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            for tarea in tareas:
                data = (
                    tarea['id_tarea'],
                    tarea['titulo'],
                    tarea['prioridad'],
                    tarea['descripcion'],
                    tarea['estado'],
                    tarea['fecha_inicio'],
                    tarea['fecha_fin']
                )
                self.cursor.execute(insert_query, data)
                self.stats['dim_tarea'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['dim_tarea']} registros en Dim_Tarea\n")
            
        except Error as e:
            print(f"✗ Error en Dim_Tarea: {e}")
            self.connection.rollback()
            raise
    
    def extraer_fact_proyectos(self):
        """Extraer y cargar fact table de proyectos con métricas calculadas"""
        print("Procesando Fact_Proyectos...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT 
                p.id_proyecto,
                p.id_cliente,
                p.id_responsable,
                p.fecha_inicio,
                p.presupuesto,
                p.costo_total,
                p.ganancia,
                p.perdida,
                p.progreso,
                p.entregables_count,
                p.horas_invertidas,
                p.defectos_detectados,
                (p.presupuesto - p.costo_total) as desviacion_presupuesto,
                CASE 
                    WHEN p.costo_total > 0 THEN ((p.ganancia - p.perdida) / p.costo_total) * 100
                    ELSE 0
                END as roi,
                DATEDIFF(p.fecha_fin, p.fecha_inicio) as desviacion_tiempo,
                COALESCE(AVG(ec.calificacion), 0) as satisfaccion_cliente,
                CASE 
                    WHEN p.entregables_count > 0 THEN p.defectos_detectados / p.entregables_count
                    ELSE 0
                END as tasa_defectos
            FROM Proyectos p
            LEFT JOIN Evaluaciones_Cliente ec ON p.id_proyecto = ec.id_proyecto
            GROUP BY p.id_proyecto
            """
            
            self.cursor.execute(query)
            proyectos = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Fact_Proyectos (
                id_proyecto, id_cliente, id_responsable, id_tiempo,
                presupuesto, costo_total, ganancia, perdida, progreso,
                entregables_count, horas_invertidas,
                desviacion_presupuesto, desviacion_tiempo,
                tasa_defectos, satisfaccion_cliente, roi
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for proy in proyectos:
                # Obtener id_tiempo
                self.cursor.execute(
                    "SELECT id_tiempo FROM Dim_Tiempo WHERE fecha = %s",
                    (proy['fecha_inicio'],)
                )
                tiempo_result = self.cursor.fetchone()
                id_tiempo = tiempo_result['id_tiempo'] if tiempo_result else None
                
                if id_tiempo:
                    data = (
                        proy['id_proyecto'],
                        proy['id_cliente'],
                        proy['id_responsable'],
                        id_tiempo,
                        proy['presupuesto'],
                        proy['costo_total'],
                        proy['ganancia'],
                        proy['perdida'],
                        proy['progreso'],
                        proy['entregables_count'],
                        proy['horas_invertidas'],
                        proy['desviacion_presupuesto'],
                        proy['desviacion_tiempo'],
                        proy['tasa_defectos'],
                        proy['satisfaccion_cliente'],
                        proy['roi']
                    )
                    self.cursor.execute(insert_query, data)
                    self.stats['fact_proyectos'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['fact_proyectos']} registros en Fact_Proyectos\n")
            
        except Error as e:
            print(f"✗ Error en Fact_Proyectos: {e}")
            self.connection.rollback()
            raise
    
    def extraer_fact_tareas(self):
        """Extraer y cargar fact table de tareas"""
        print("Procesando Fact_Tareas...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT 
                t.id_tarea,
                t.id_proyecto,
                t.fecha_inicio,
                t.horas_estimadas,
                t.horas_reales,
                t.estado,
                (t.horas_reales - t.horas_estimadas) as desviacion_horas,
                p.id_responsable
            FROM Tareas t
            JOIN Proyectos p ON t.id_proyecto = p.id_proyecto
            """
            
            self.cursor.execute(query)
            tareas = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Fact_Tareas (
                id_tarea, id_proyecto, id_tiempo, horas_estimadas, 
                horas_reales, estado, desviacion_horas, id_responsable
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for tarea in tareas:
                # Obtener id_tiempo
                self.cursor.execute(
                    "SELECT id_tiempo FROM Dim_Tiempo WHERE fecha = %s",
                    (tarea['fecha_inicio'],)
                )
                tiempo_result = self.cursor.fetchone()
                id_tiempo = tiempo_result['id_tiempo'] if tiempo_result else None
                
                if id_tiempo:
                    data = (
                        tarea['id_tarea'],
                        tarea['id_proyecto'],
                        id_tiempo,
                        tarea['horas_estimadas'],
                        tarea['horas_reales'],
                        tarea['estado'],
                        tarea['desviacion_horas'],
                        tarea['id_responsable']
                    )
                    self.cursor.execute(insert_query, data)
                    self.stats['fact_tareas'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['fact_tareas']} registros en Fact_Tareas\n")
            
        except Error as e:
            print(f"✗ Error en Fact_Tareas: {e}")
            self.connection.rollback()
            raise
    
    def extraer_fact_tiempo_trabajo(self):
        """Extraer y cargar fact table de tiempo de trabajo"""
        print("Procesando Fact_Tiempo_Trabajo...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT 
                id_responsable,
                id_tarea,
                fecha,
                TIME_TO_SEC(horasTrabajadas) / 3600 as horas_trabajadas
            FROM Registro_Tiempo
            """
            
            self.cursor.execute(query)
            registros = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Fact_Tiempo_Trabajo (id_responsable, id_tarea, id_tiempo, horas_trabajadas)
            VALUES (%s, %s, %s, %s)
            """
            
            for reg in registros:
                # Obtener id_tiempo
                self.cursor.execute(
                    "SELECT id_tiempo FROM Dim_Tiempo WHERE fecha = %s",
                    (reg['fecha'],)
                )
                tiempo_result = self.cursor.fetchone()
                id_tiempo = tiempo_result['id_tiempo'] if tiempo_result else None
                
                if id_tiempo:
                    data = (
                        reg['id_responsable'],
                        reg['id_tarea'],
                        id_tiempo,
                        reg['horas_trabajadas']
                    )
                    self.cursor.execute(insert_query, data)
                    self.stats['fact_tiempo_trabajo'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['fact_tiempo_trabajo']} registros en Fact_Tiempo_Trabajo\n")
            
        except Error as e:
            print(f"✗ Error en Fact_Tiempo_Trabajo: {e}")
            self.connection.rollback()
            raise
    
    def extraer_fact_costos(self):
        """Extraer y cargar fact table de costos"""
        print("Procesando Fact_Costos...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT 
                id_proyecto,
                fecha,
                tipo,
                proveedor,
                monto,
                moneda
            FROM Costos
            """
            
            self.cursor.execute(query)
            costos = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Fact_Costos (id_proyecto, id_tiempo, tipo, proveedor, monto, moneda)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            for costo in costos:
                # Obtener id_tiempo
                self.cursor.execute(
                    "SELECT id_tiempo FROM Dim_Tiempo WHERE fecha = %s",
                    (costo['fecha'],)
                )
                tiempo_result = self.cursor.fetchone()
                id_tiempo = tiempo_result['id_tiempo'] if tiempo_result else None
                
                if id_tiempo:
                    data = (
                        costo['id_proyecto'],
                        id_tiempo,
                        costo['tipo'],
                        costo['proveedor'],
                        costo['monto'],
                        costo['moneda']
                    )
                    self.cursor.execute(insert_query, data)
                    self.stats['fact_costos'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['fact_costos']} registros en Fact_Costos\n")
            
        except Error as e:
            print(f"✗ Error en Fact_Costos: {e}")
            self.connection.rollback()
            raise
    
    def extraer_fact_defectos(self):
        """Extraer y cargar fact table de defectos desde tabla Defectos"""
        print("Procesando Fact_Defectos...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT 
                id_proyecto,
                DATE(fecha_deteccion) as fecha,
                tipo_defecto,
                severidad,
                estado,
                etapa_deteccion,
                DATEDIFF(COALESCE(fecha_correccion, CURDATE()), fecha_deteccion) as dias_correccion
            FROM Defectos
            WHERE fecha_deteccion IS NOT NULL
            """
            
            self.cursor.execute(query)
            defectos = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Fact_Defectos (id_proyecto, id_tiempo, cantidad, tipo_defecto, 
                                      severidad, estado_defecto, etapa_deteccion, dias_correccion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for defecto in defectos:
                # Obtener id_tiempo
                self.cursor.execute(
                    "SELECT id_tiempo FROM Dim_Tiempo WHERE fecha = %s",
                    (defecto['fecha'],)
                )
                tiempo_result = self.cursor.fetchone()
                id_tiempo = tiempo_result['id_tiempo'] if tiempo_result else None
                
                if id_tiempo:
                    data = (
                        defecto['id_proyecto'],
                        id_tiempo,
                        1,  # Cada registro es 1 defecto
                        defecto['tipo_defecto'],
                        defecto['severidad'],
                        defecto['estado'],
                        defecto['etapa_deteccion'],
                        defecto['dias_correccion'] if defecto['dias_correccion'] else None
                    )
                    self.cursor.execute(insert_query, data)
                    self.stats['fact_defectos'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['fact_defectos']} registros en Fact_Defectos\n")
            
        except Error as e:
            print(f"✗ Error en Fact_Defectos: {e}")
            self.connection.rollback()
            raise
    
    def extraer_fact_incidencias(self):
        """Extraer y cargar fact table de incidencias"""
        print("Procesando Fact_Incidencias...")
        try:
            self.cursor.execute("USE SG_Proyectos")
            
            query = """
            SELECT 
                id_proyecto,
                id_tarea,
                id_responsable,
                fecha_reporte,
                severidad,
                estado,
                DATEDIFF(fecha_resolucion, fecha_reporte) as dias_resolucion
            FROM Incidencias
            """
            
            self.cursor.execute(query)
            incidencias = self.cursor.fetchall()
            
            self.cursor.execute("USE DSS_Proyectos")
            
            insert_query = """
            INSERT INTO Fact_Incidencias (
                id_proyecto, id_tarea, id_responsable, id_tiempo,
                severidad, estado, dias_resolucion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            for inc in incidencias:
                # Obtener id_tiempo
                self.cursor.execute(
                    "SELECT id_tiempo FROM Dim_Tiempo WHERE fecha = %s",
                    (inc['fecha_reporte'],)
                )
                tiempo_result = self.cursor.fetchone()
                id_tiempo = tiempo_result['id_tiempo'] if tiempo_result else None
                
                if id_tiempo:
                    data = (
                        inc['id_proyecto'],
                        inc['id_tarea'],
                        inc['id_responsable'],
                        id_tiempo,
                        inc['severidad'],
                        inc['estado'],
                        inc['dias_resolucion']
                    )
                    self.cursor.execute(insert_query, data)
                    self.stats['fact_incidencias'] += 1
            
            self.connection.commit()
            print(f"✓ {self.stats['fact_incidencias']} registros en Fact_Incidencias\n")
            
        except Error as e:
            print(f"✗ Error en Fact_Incidencias: {e}")
            self.connection.rollback()
            raise
    
    def ejecutar_etl(self):
        """Ejecutar todo el proceso ETL"""
        print("\n" + "="*70)
        print(" PROCESO ETL: SG_Proyectos → DSS_Proyectos")
        print("="*70 + "\n")
        
        inicio = datetime.now()
        
        try:
            # 1. Limpiar DSS
            self.limpiar_dss()
            
            # 2. Cargar dimensiones
            print("FASE 1: CARGANDO DIMENSIONES")
            print("-" * 70)
            self.extraer_dim_tiempo()
            self.extraer_dim_cliente()
            self.extraer_dim_responsable()
            self.extraer_dim_proyecto()
            self.extraer_dim_tarea()
            
            # 3. Cargar hechos
            print("\nFASE 2: CARGANDO TABLAS DE HECHOS")
            print("-" * 70)
            self.extraer_fact_proyectos()
            self.extraer_fact_tareas()
            self.extraer_fact_tiempo_trabajo()
            self.extraer_fact_costos()
            self.extraer_fact_defectos()
            self.extraer_fact_incidencias()
            
            fin = datetime.now()
            duracion = (fin - inicio).total_seconds()
            
            # Resumen
            print("\n" + "="*70)
            print(" RESUMEN DEL ETL")
            print("="*70)
            print(f"\n✓ ETL completado exitosamente en {duracion:.2f} segundos\n")
            print("Registros procesados:")
            print(f"  • Dim_Tiempo:          {self.stats['dim_tiempo']:>6}")
            print(f"  • Dim_Cliente:         {self.stats['dim_cliente']:>6}")
            print(f"  • Dim_Responsable:     {self.stats['dim_responsable']:>6}")
            print(f"  • Dim_Proyecto:        {self.stats['dim_proyecto']:>6}")
            print(f"  • Dim_Tarea:           {self.stats['dim_tarea']:>6}")
            print(f"  • Fact_Proyectos:      {self.stats['fact_proyectos']:>6}")
            print(f"  • Fact_Tareas:         {self.stats['fact_tareas']:>6}")
            print(f"  • Fact_Tiempo_Trabajo: {self.stats['fact_tiempo_trabajo']:>6}")
            print(f"  • Fact_Costos:         {self.stats['fact_costos']:>6}")
            print(f"  • Fact_Defectos:       {self.stats['fact_defectos']:>6}")
            print(f"  • Fact_Incidencias:    {self.stats['fact_incidencias']:>6}")
            print("\n" + "="*70)
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error durante el ETL: {e}")
            return False

def main():
    """Función principal"""
    etl = ETLProcessor(DB_CONFIG)
    
    try:
        if etl.connect():
            exito = etl.ejecutar_etl()
            if exito:
                print("\n✓ Proceso ETL finalizado correctamente")
                print("✓ El DSS está listo para consultas y análisis")
            else:
                print("\n✗ El proceso ETL finalizó con errores")
    except KeyboardInterrupt:
        print("\n\n✗ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
    finally:
        etl.disconnect()

if __name__ == "__main__":
    main()