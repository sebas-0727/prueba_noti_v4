import threading
import time
import webbrowser
import pymysql
from flask import Flask, render_template
from notifypy import Notify

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'rasc',
    'port': 3306,
    'cursorclass': pymysql.cursors.DictCursor
}

app = Flask(__name__)

notificacion_mostrada = False  # Variable para rastrear si la notificación ya fue mostrada

# URL a abrir
url_a_abrir = "http://tusitio.com"  # Cambia esto a la URL deseada

def obtener_ultimo_numero():
    with pymysql.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(numero) as max_numero FROM reporte")
            resultado = cursor.fetchone()
            return resultado['max_numero'] if resultado['max_numero'] is not None else 0

def verificar_nuevos_registros(ultimo_numero_conocido):
    with pymysql.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reporte WHERE numero > %s", (ultimo_numero_conocido,))
            return cursor.fetchall()

def abrir_url():
    webbrowser.open(url_a_abrir)  # Abre la URL en el navegador

def enviar_notificacion(registro):
    global notificacion_mostrada  # Usamos la variable global

    if not notificacion_mostrada:  # Solo mostramos la notificación si no se ha mostrado antes
        notificacion = Notify()
        notificacion.title = f"Nuevo reporte en: {registro['zona']}"
        notificacion.message = f"Hora: {registro['hora']}\nAtaque: {registro['ataco']}\nObservaciones: {registro['observaciones']}"
        notificacion.icon = "./templates/imagen_prueba.png"  # Asegúrate de que esta ruta sea válida
        notificacion.send()
        
        notificacion_mostrada = True  # Marcamos que la notificación ha sido mostrada

        # Abre la URL después de enviar la notificación
        abrir_url()
        
        # Función para restablecer la variable después de 5 segundos
        threading.Timer(5, reset_notificacion).start()

def reset_notificacion():
    global notificacion_mostrada
    notificacion_mostrada = False  # Reiniciamos la variable

def monitor():
    ultimo_numero_conocido = obtener_ultimo_numero()
    print("Monitoreando nuevos registros...")

    while True:
        nuevos_registros = verificar_nuevos_registros(ultimo_numero_conocido)
        for registro in nuevos_registros:
            enviar_notificacion(registro)
            ultimo_numero_conocido = registro['numero']
        
        time.sleep(3)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    threading.Thread(target=monitor, daemon=True).start()
    app.run(debug=True)
