#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'fitboost_colombia_secret_key_2024'
app.config['DATABASE'] = 'fitboost.db'

# ============================================================
# UTILIDADES
# ============================================================

def safe_float(val):
    if not val: return 0.0
    try: return float(val)
    except (ValueError, TypeError): return 0.0

def safe_int(val):
    if not val: return 0
    try: return int(val)
    except (ValueError, TypeError): return 0

# ============================================================
# BASE DE DATOS
# ============================================================

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def crear_base_datos():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rutinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        variante TEXT NOT NULL,
        objetivo TEXT,
        descripcion TEXT,
        UNIQUE(nombre, variante)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ejercicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rutina_id INTEGER,
        dia TEXT,
        orden INTEGER,
        nombre_ejercicio TEXT NOT NULL,
        series TEXT,
        repeticiones TEXT,
        descanso TEXT,
        FOREIGN KEY (rutina_id) REFERENCES rutinas(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios_planes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        nombre TEXT,
        rutina_sugerida TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    return conn

def insertar_rutina(cursor, nombre, variante, objetivo, descripcion, ejercicios):
    cursor.execute('INSERT OR IGNORE INTO rutinas (nombre, variante, objetivo, descripcion) VALUES (?, ?, ?, ?)', 
                   (nombre, variante, objetivo, descripcion))
    
    cursor.execute('SELECT id FROM rutinas WHERE nombre = ? AND variante = ?', (nombre, variante))
    rutina_id = cursor.fetchone()[0]
    
    cursor.execute('DELETE FROM ejercicios WHERE rutina_id = ?', (rutina_id,))
    
    for ej in ejercicios:
        cursor.execute('''
            INSERT INTO ejercicios (rutina_id, dia, orden, nombre_ejercicio, series, repeticiones, descanso)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (rutina_id, ej['dia'], ej['orden'], ej['nombre'], ej['series'], ej['reps'], ej.get('descanso', '')))

def poblar_rutinas(conn):
    cursor = conn.cursor()

    # --- FULL BODY ---
    insertar_rutina(cursor, "Full Body", "Casa", "Hipertrofia general", "Ideal para principiantes.", [
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 1, 'nombre': 'Flexiones de pecho', 'series': '4', 'reps': '10-15', 'descanso': '60s'},
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 2, 'nombre': 'Sentadillas (Peso corporal)', 'series': '4', 'reps': '15-20', 'descanso': '60s'},
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 3, 'nombre': 'Fondos entre sillas', 'series': '3', 'reps': '10-12', 'descanso': '60s'},
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 4, 'nombre': 'Remo invertido en mesa', 'series': '3', 'reps': '12-15', 'descanso': '60s'},
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 5, 'nombre': 'Zancadas alternas', 'series': '3', 'reps': '12 c/pierna', 'descanso': '60s'},
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 6, 'nombre': 'Plancha frontal', 'series': '3', 'reps': '30-45s', 'descanso': '45s'},
    ])

    insertar_rutina(cursor, "Full Body", "Gimnasio", "Hipertrofia con compuestos", "Rutina completa de fuerza.", [
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 1, 'nombre': 'Press de banca con barra', 'series': '4', 'reps': '8-10', 'descanso': '90s'},
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 2, 'nombre': 'Sentadilla con barra', 'series': '4', 'reps': '8-10', 'descanso': '90s'},
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 3, 'nombre': 'Peso muerto convencional', 'series': '3', 'reps': '6-8', 'descanso': '120s'},
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 4, 'nombre': 'Dominadas', 'series': '3', 'reps': '10-12', 'descanso': '90s'},
        {'dia': 'Día 1: Cuerpo Completo', 'orden': 5, 'nombre': 'Press militar mancuernas', 'series': '3', 'reps': '10-12', 'descanso': '60s'},
    ])

    # --- UPPER-LOWER ---
    insertar_rutina(cursor, "Upper-Lower", "Casa", "Entrenamiento dividido", "Frecuencia 2 optimizada para casa.", [
        # Día 1 Upper
        {'dia': 'Día 1: Torso (Upper)', 'orden': 1, 'nombre': 'Flexiones clásicas', 'series': '4', 'reps': '12-15', 'descanso': '60s'},
        {'dia': 'Día 1: Torso (Upper)', 'orden': 2, 'nombre': 'Fondos entre sillas', 'series': '3', 'reps': '10-12', 'descanso': '60s'},
        {'dia': 'Día 1: Torso (Upper)', 'orden': 3, 'nombre': 'Remo con mochila', 'series': '4', 'reps': '12', 'descanso': '60s'},
        {'dia': 'Día 1: Torso (Upper)', 'orden': 4, 'nombre': 'Elevaciones laterales', 'series': '3', 'reps': '15', 'descanso': '45s'},
        # Día 2 Lower
        {'dia': 'Día 2: Pierna (Lower)', 'orden': 1, 'nombre': 'Sentadillas con mochila', 'series': '4', 'reps': '15-20', 'descanso': '90s'},
        {'dia': 'Día 2: Pierna (Lower)', 'orden': 2, 'nombre': 'Zancadas', 'series': '4', 'reps': '12 c/pierna', 'descanso': '60s'},
        {'dia': 'Día 2: Pierna (Lower)', 'orden': 3, 'nombre': 'Peso muerto rumano', 'series': '3', 'reps': '12-15', 'descanso': '60s'},
        {'dia': 'Día 2: Pierna (Lower)', 'orden': 4, 'nombre': 'Puente de glúteos', 'series': '3', 'reps': '15-20', 'descanso': '45s'}
    ])

    insertar_rutina(cursor, "Upper-Lower", "Gimnasio", "Entrenamiento dividido", "Fuerza e hipertrofia.", [
        # Día 1 Upper
        {'dia': 'Día 1: Torso (Upper)', 'orden': 1, 'nombre': 'Press de banca', 'series': '4', 'reps': '8-10', 'descanso': '90s'},
        {'dia': 'Día 1: Torso (Upper)', 'orden': 2, 'nombre': 'Press militar', 'series': '3', 'reps': '10-12', 'descanso': '90s'},
        {'dia': 'Día 1: Torso (Upper)', 'orden': 3, 'nombre': 'Dominadas', 'series': '4', 'reps': '10-12', 'descanso': '90s'},
        # Día 2 Lower
        {'dia': 'Día 2: Pierna (Lower)', 'orden': 1, 'nombre': 'Sentadilla con barra', 'series': '4', 'reps': '8-10', 'descanso': '120s'},
        {'dia': 'Día 2: Pierna (Lower)', 'orden': 2, 'nombre': 'Peso muerto rumano', 'series': '4', 'reps': '8-10', 'descanso': '90s'},
        {'dia': 'Día 2: Pierna (Lower)', 'orden': 3, 'nombre': 'Prensa de piernas', 'series': '3', 'reps': '12', 'descanso': '90s'},
    ])

    # --- ARNOLD SPLIT ---
    insertar_rutina(cursor, "Arnold Split", "Casa", "Pecho/Espalda, Hombro/Brazo, Pierna", "La división clásica de Arnold.", [
        # Día 1
        {'dia': 'Día 1: Pecho y Espalda', 'orden': 1, 'nombre': 'Flexiones', 'series': '4', 'reps': '15', 'descanso': '60s'},
        {'dia': 'Día 1: Pecho y Espalda', 'orden': 2, 'nombre': 'Remo con mochila', 'series': '4', 'reps': '12', 'descanso': '60s'},
        {'dia': 'Día 1: Pecho y Espalda', 'orden': 3, 'nombre': 'Fondos', 'series': '3', 'reps': '12', 'descanso': '60s'},
        # Día 2
        {'dia': 'Día 2: Hombro y Brazo', 'orden': 1, 'nombre': 'Elevaciones laterales', 'series': '4', 'reps': '15', 'descanso': '45s'},
        {'dia': 'Día 2: Hombro y Brazo', 'orden': 2, 'nombre': 'Flexiones diamante', 'series': '3', 'reps': '12', 'descanso': '60s'},
        {'dia': 'Día 2: Hombro y Brazo', 'orden': 3, 'nombre': 'Curl bíceps', 'series': '3', 'reps': '15', 'descanso': '45s'},
        # Día 3
        {'dia': 'Día 3: Pierna', 'orden': 1, 'nombre': 'Sentadillas', 'series': '4', 'reps': '20', 'descanso': '90s'},
        {'dia': 'Día 3: Pierna', 'orden': 2, 'nombre': 'Zancadas', 'series': '4', 'reps': '12 c/pierna', 'descanso': '60s'},
    ])
    
    insertar_rutina(cursor, "Arnold Split", "Gimnasio", "Alta intensidad", "Enfoque en antagonistas.", [
        {'dia': 'Día 1: Pecho y Espalda', 'orden': 1, 'nombre': 'Press Banca', 'series': '4', 'reps': '8-10', 'descanso': '90s'},
        {'dia': 'Día 1: Pecho y Espalda', 'orden': 2, 'nombre': 'Dominadas', 'series': '4', 'reps': '10-12', 'descanso': '90s'},
        {'dia': 'Día 2: Hombro y Brazo', 'orden': 1, 'nombre': 'Press Militar', 'series': '4', 'reps': '8-10', 'descanso': '90s'},
        {'dia': 'Día 2: Hombro y Brazo', 'orden': 2, 'nombre': 'Curl Barra', 'series': '4', 'reps': '10-12', 'descanso': '60s'},
        {'dia': 'Día 3: Pierna', 'orden': 1, 'nombre': 'Sentadilla', 'series': '4', 'reps': '8-10', 'descanso': '120s'},
    ])

    # --- BRO SPLIT ---
    insertar_rutina(cursor, "Bro Split", "Casa", "Un músculo por día", "Foco máximo en cada grupo.", [
        {'dia': 'Lunes: Pecho', 'orden': 1, 'nombre': 'Flexiones clásicas', 'series': '4', 'reps': '15-20', 'descanso': '60s'},
        {'dia': 'Lunes: Pecho', 'orden': 2, 'nombre': 'Flexiones declinadas', 'series': '3', 'reps': '12-15', 'descanso': '60s'},
        {'dia': 'Martes: Espalda', 'orden': 1, 'nombre': 'Remo mochila', 'series': '4', 'reps': '15', 'descanso': '60s'},
        {'dia': 'Miércoles: Pierna', 'orden': 1, 'nombre': 'Sentadillas', 'series': '4', 'reps': '20', 'descanso': '90s'},
        {'dia': 'Jueves: Hombro', 'orden': 1, 'nombre': 'Pike push-ups', 'series': '3', 'reps': '10-12', 'descanso': '60s'},
        {'dia': 'Viernes: Brazos', 'orden': 1, 'nombre': 'Curl + Fondos', 'series': '4', 'reps': '15', 'descanso': '60s'}
    ])

    insertar_rutina(cursor, "Bro Split", "Gimnasio", "Un músculo por día", "Foco máximo en cada grupo.", [
        {'dia': 'Lunes: Pecho', 'orden': 1, 'nombre': 'Press Banca', 'series': '4', 'reps': '8-10', 'descanso': '90s'},
        {'dia': 'Martes: Espalda', 'orden': 1, 'nombre': 'Jalón al pecho', 'series': '4', 'reps': '10-12', 'descanso': '90s'},
        {'dia': 'Miércoles: Pierna', 'orden': 1, 'nombre': 'Sentadilla', 'series': '4', 'reps': '8-10', 'descanso': '120s'},
        {'dia': 'Jueves: Hombro', 'orden': 1, 'nombre': 'Press Militar', 'series': '4', 'reps': '10', 'descanso': '90s'},
        {'dia': 'Viernes: Brazos', 'orden': 1, 'nombre': 'Curl Barra + Press Francés', 'series': '4', 'reps': '12', 'descanso': '60s'}
    ])

    # --- PUSH PULL LEGS ---
    insertar_rutina(cursor, "Push Pull Legs", "Gimnasio", "Frecuencia alta", "La más popular.", [
        {'dia': 'Día 1: Push (Empuje)', 'orden': 1, 'nombre': 'Press Banca', 'series': '4', 'reps': '8-10', 'descanso': '90s'},
        {'dia': 'Día 1: Push (Empuje)', 'orden': 2, 'nombre': 'Press Inclinado', 'series': '3', 'reps': '10-12', 'descanso': '90s'},
        {'dia': 'Día 2: Pull (Tracción)', 'orden': 1, 'nombre': 'Dominadas', 'series': '4', 'reps': 'Fallos', 'descanso': '90s'},
        {'dia': 'Día 2: Pull (Tracción)', 'orden': 2, 'nombre': 'Remo con mancuerna', 'series': '3', 'reps': '12', 'descanso': '60s'},
        {'dia': 'Día 3: Legs (Pierna)', 'orden': 1, 'nombre': 'Sentadilla', 'series': '4', 'reps': '8-10', 'descanso': '120s'},
        {'dia': 'Día 3: Legs (Pierna)', 'orden': 2, 'nombre': 'Extensiones', 'series': '3', 'reps': '15', 'descanso': '60s'}
    ])

    conn.commit()
    print("✅ Base de datos restaurada con TODAS las rutinas y días corregidos.")

# ============================================================
# CLASES
# ============================================================

class Usuario:
    def __init__(self, data=None):
        if data:
            self.nombre = data.get('nombre', '')
            self.sexo = safe_int(data.get('sexo'))
            self.edad = safe_int(data.get('edad'))
            self.peso_kg = safe_float(data.get('peso_kg'))
            self.altura_m = safe_float(data.get('altura_m'))
            self.nivel_actividad = data.get('nivel_actividad', '')
            self.multiplicador_actividad = safe_float(data.get('multiplicador_actividad'))
            self.dias_entrenamiento = safe_int(data.get('dias_entrenamiento'))
            self.duracion_entrenamiento = safe_int(data.get('duracion_entrenamiento'))
            self.objetivo = data.get('objetivo', '')
            self.usar_suplementos = data.get('usar_suplementos')
            self.presupuesto_suplementos = safe_float(data.get('presupuesto_suplementos'))
            self.recordatorio_agua = data.get('recordatorio_agua')
            self.intervalo_agua = safe_float(data.get('intervalo_agua'))
            self.recordatorio_ejercicio = data.get('recordatorio_ejercicio')
            self.intervalo_ejercicio = safe_float(data.get('intervalo_ejercicio'))
            self.rutina_sugerida = data.get('rutina_sugerida', '')

    def calcular_calorias(self):
        altura_cm = self.altura_m * 100
        if self.sexo == 1: val = 5
        else: val = -161
        
        bmr = 10 * self.peso_kg + 6.25 * altura_cm - 5 * self.edad + val
        tdee = bmr * (self.multiplicador_actividad or 1.2)
        
        if self.objetivo == "Bajar de peso": meta = max(1200, tdee - 500)
        elif self.objetivo == "Ganar masa muscular": meta = tdee + 300
        else: meta = tdee
        return tdee, meta

    def calcular_imc(self):
        if self.altura_m > 0: return self.peso_kg / (self.altura_m ** 2)
        return 0

class GestorRutinas:
    def obtener_todas_rutinas(self):
        conn = get_db_connection()
        rutinas = conn.execute('SELECT nombre, variante, objetivo FROM rutinas').fetchall()
        conn.close()
        return [dict(r) for r in rutinas]

    def obtener_nombres_rutinas(self):
        conn = get_db_connection()
        nombres = conn.execute('SELECT DISTINCT nombre FROM rutinas ORDER BY nombre').fetchall()
        conn.close()
        return [n[0] for n in nombres]

    def obtener_rutina_con_ejercicios(self, nombre, variante):
        conn = get_db_connection()
        rutina = conn.execute('SELECT * FROM rutinas WHERE nombre = ? AND variante = ?', (nombre, variante)).fetchone()
        
        if not rutina:
            conn.close()
            return None
            
        res = dict(rutina)
        # Ordenar por día y luego por número de orden para que el agrupamiento visual funcione bien
        ejercicios = conn.execute('SELECT * FROM ejercicios WHERE rutina_id = ? ORDER BY dia, orden', (rutina['id'],)).fetchall()
        res['ejercicios'] = [dict(e) for e in ejercicios]
        conn.close()
        return res

# ============================================================
# RUTAS
# ============================================================

@app.route('/')
def index(): return render_template('index.html')

@app.route('/planificador', methods=['GET', 'POST'])
def planificador():
    if request.method == 'POST':
        usuario_data = {
            'nombre': request.form.get('nombre'),
            'sexo': request.form.get('sexo'),
            'edad': request.form.get('edad'),
            'peso_kg': request.form.get('peso_kg'),
            'altura_m': request.form.get('altura_m'),
            'nivel_actividad': request.form.get('nivel_actividad'),
            'multiplicador_actividad': request.form.get('multiplicador_actividad'),
            'dias_entrenamiento': request.form.get('dias_entrenamiento'),
            'duracion_entrenamiento': request.form.get('duracion_entrenamiento'),
            'objetivo': request.form.get('objetivo'),
            'usar_suplementos': request.form.get('usar_suplementos') == 'true',
            'presupuesto_suplementos': request.form.get('presupuesto_suplementos'),
            'recordatorio_agua': request.form.get('recordatorio_agua') == 'true',
            'intervalo_agua': request.form.get('intervalo_agua'),
            'recordatorio_ejercicio': request.form.get('recordatorio_ejercicio') == 'true',
            'intervalo_ejercicio': request.form.get('intervalo_ejercicio')
        }
        
        dias = safe_int(usuario_data['dias_entrenamiento'])
        if dias <= 2: usuario_data['rutina_sugerida'] = "Full Body"
        elif dias <= 4: usuario_data['rutina_sugerida'] = "Upper-Lower"
        elif dias == 5: usuario_data['rutina_sugerida'] = "Arnold Split"
        else: usuario_data['rutina_sugerida'] = "Push Pull Legs"
        
        session['usuario_actual'] = usuario_data
        return redirect(url_for('resumen'))
    return render_template('planificador.html')

@app.route('/resumen')
def resumen():
    data = session.get('usuario_actual')
    if not data: return redirect(url_for('planificador'))
    
    usuario = Usuario(data)
    tdee, meta = usuario.calcular_calorias()
    imc = usuario.calcular_imc()
    
    if imc < 18.5: clasif = "Bajo peso"
    elif imc < 25: clasif = "Normal"
    elif imc < 30: clasif = "Sobrepeso"
    else: clasif = "Obesidad"
    
    return render_template('resumen.html', usuario=usuario, tdee=tdee, meta_calorias=meta, imc=imc, clasif_imc=clasif)

@app.route('/rutinas')
def rutinas():
    gestor = GestorRutinas()
    return render_template('rutinas.html', rutinas=gestor.obtener_todas_rutinas(), nombres_rutinas=gestor.obtener_nombres_rutinas())

@app.route('/rutina/<nombre>/<variante>')
def rutina_detalle(nombre, variante):
    gestor = GestorRutinas()
    rutina = gestor.obtener_rutina_con_ejercicios(nombre, variante)
    if not rutina: return "Rutina no encontrada", 404
    return render_template('rutina_detalle.html', rutina=rutina)

if __name__ == '__main__':
    if not os.path.exists(app.config['DATABASE']):
        conn = crear_base_datos()
        poblar_rutinas(conn)
        conn.close()
    app.run(debug=True, host='0.0.0.0', port=5000)