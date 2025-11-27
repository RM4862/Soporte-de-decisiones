import subprocess
import sys
import os
import time
import mysql.connector
from mysql.connector import Error

# --- CONFIGURACIÓN DE ARCHIVOS ---
# Asegúrate de que los nombres coincidan exactamente con tus archivos
FILES = {
    'sql_sg': 'SG_proyectos (2).sql',   # Base de datos Transaccional
    'sql_dss': 'DSS_proyectos (2).sql', # Data Warehouse
    'generator': 'generar_datos (1).py',    # Generador de datos
    'etl': 'etl.py',                    # Proceso ETL
    'trainer': 'train_rayleigh.py',     # Entrenamiento del modelo
    'api': 'rayleigh_api.py'            # Servidor API
}

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '' # Agrega tu contraseña si es necesaria
}

def print_header(msg):
    print("\n" + "="*60)
    print(f"PROCESO: {msg}")
    print("="*60)

def run_sql_file(filename):
    """Lee y ejecuta un archivo .sql directamente en MySQL."""
    print(f"   [SQL] Ejecutando script: {filename}...")
    
    if not os.path.exists(filename):
        print(f"   [ERROR] No se encuentra el archivo: {filename}")
        return False

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        with open(filename, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # Separar comandos por punto y coma
        commands = sql_content.split(';')
        
        for command in commands:
            if command.strip():
                try:
                    cursor.execute(command)
                except Error as err:
                    # Ignorar advertencias de tablas existentes si usas IF NOT EXISTS
                    if err.errno != 1050: 
                        print(f"   [ADVERTENCIA] {err}")

        conn.commit()
        cursor.close()
        conn.close()
        print("   [OK] Base de datos actualizada correctamente.")
        return True
    except Error as e:
        print(f"   [ERROR CRITICO SQL] {e}")
        return False

def run_python_script(filename):
    """Ejecuta un script de Python y espera a que termine."""
    print(f"   [PYTHON] Ejecutando: {filename}...")
    
    if not os.path.exists(filename):
        print(f"   [ADVERTENCIA] No se encontro {filename}, saltando este paso.")
        # Retornamos True para no detener el flujo completo si falta un archivo opcional
        return True 

    try:
        # sys.executable asegura que usamos el mismo intérprete python actual
        subprocess.run([sys.executable, filename], capture_output=False, check=True)
        print(f"   [OK] {filename} finalizado con exito.")
        return True
    except subprocess.CalledProcessError:
        print(f"   [ERROR] Fallo la ejecucion de {filename}.")
        return False

def main():
    print_header("INICIANDO CONFIGURACION AUTOMATICA DEL SISTEMA")

    # 1. Restaurar Estructura de Base de Datos (SQL)
    print_header("PASO 1: Creando Tablas (SG y DSS)")
    if not run_sql_file(FILES['sql_sg']): return
    if not run_sql_file(FILES['sql_dss']): return

    # 2. Generar Datos Sintéticos
    print_header("PASO 2: Generando Datos de Prueba (SG)")
    if not run_python_script(FILES['generator']): return

    # 3. Correr ETL (Mover datos a OLAP)
    print_header("PASO 3: Ejecutando ETL (Carga al Data Warehouse)")
    run_python_script(FILES['etl'])

    # 4. Entrenar Modelo Predictivo
    print_header("PASO 4: Entrenando Modelo Rayleigh")
    if not run_python_script(FILES['trainer']): return

    # 5. Iniciar Servidor API
    print_header("PASO 5: Iniciando Servidor Backend")
    print("   [INFO] El servidor se esta iniciando en el puerto 5000...")
    print("   [INFO] Presiona CTRL+C para detener el servidor y salir.")
    
    try:
        # Popen inicia el proceso sin bloquear el script actual
        server_process = subprocess.Popen([sys.executable, FILES['api']])
        server_process.wait() # Mantiene el script vivo mientras el servidor corre
    except KeyboardInterrupt:
        print("\n   [DETENIENDO] Cerrando servidor...")
        server_process.terminate()
        print("   [SALIR] Hasta luego.")

if __name__ == "__main__":
    main()