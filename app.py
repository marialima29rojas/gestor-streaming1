<<<<<<< HEAD
import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

def conectar_db():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# Las tablas ya están creadas, así que no tocamos init_db

@app.route('/')
def index():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT id, plataforma, correo, password, vencimiento FROM cuentas ORDER BY vencimiento ASC')
    cuentas_raw = cur.fetchall()
    lista_cuentas = []
    hoy = datetime.now().date()
    for c in cuentas_raw:
        dias_restantes = (c[4] - hoy).days if c[4] else 0
        cur.execute('SELECT nombre_usuario, pin, contacto, id FROM perfiles WHERE id_cuenta = %s', (c[0],))
        perfiles = cur.fetchall()
        lista_cuentas.append({
            'id': c[0], 'plataforma': c[1], 'correo': c[2], 
            'password': c[3], 'vencimiento': c[4], 
            'dias': dias_restantes, 'perfiles': perfiles
        })
    cur.close()
    conn.close()
    return render_template('index.html', cuentas=lista_cuentas)

@app.route('/agregar_cuenta', methods=['POST'])
def agregar_cuenta():
    plataforma = request.form['plataforma']
    correo = request.form['correo']
    password = request.form['password']
    vencimiento = request.form['vencimiento'] or None
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO cuentas (plataforma, correo, password, vencimiento) VALUES (%s, %s, %s, %s)',
                (plataforma, correo, password, vencimiento))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/agregar_perfil', methods=['POST'])
def agregar_perfil():
    id_cuenta = request.form['id_cuenta']
    nombre = request.form['nombre']
    pin = request.form['pin']
    contacto = request.form['contacto']
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO perfiles (id_cuenta, nombre_usuario, pin, contacto) VALUES (%s, %s, %s, %s)',
                (id_cuenta, nombre, pin, contacto))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/eliminar_cuenta/<int:id>')
def eliminar_cuenta(id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM cuentas WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
=======
import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

def conectar_db():
    # Usamos la variable de entorno DATABASE_URL que pondrás en Render
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def init_db():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cuentas (
            id SERIAL PRIMARY KEY,
            plataforma TEXT NOT NULL,
            correo TEXT NOT NULL,
            password TEXT NOT NULL,
            vencimiento DATE
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS perfiles (
            id SERIAL PRIMARY KEY,
            id_cuenta INTEGER REFERENCES cuentas(id) ON DELETE CASCADE,
            nombre_usuario TEXT,
            pin TEXT,
            contacto TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Inicializamos las tablas al arrancar
init_db()

@app.route('/')
def index():
    try:
        conn = conectar_db()
        cur = conn.cursor()
        # Ordenamos por fecha: los que van a vencer primero salen arriba
        cur.execute('SELECT id, plataforma, correo, password, vencimiento FROM cuentas ORDER BY vencimiento ASC')
        cuentas_raw = cur.fetchall()
        
        lista_cuentas = []
        hoy = datetime.now().date()
        
        for c in cuentas_raw:
            # Si no hay fecha, ponemos 0 días
            dias_restantes = (c[4] - hoy).days if c[4] else 0
            
            cur.execute('SELECT nombre_usuario, pin, contacto, id FROM perfiles WHERE id_cuenta = %s', (c[0],))
            perfiles = cur.fetchall()
            
            lista_cuentas.append({
                'id': c[0], 
                'plataforma': c[1], 
                'correo': c[2], 
                'password': c[3], 
                'vencimiento': c[4], 
                'dias': dias_restantes, 
                'perfiles': perfiles
            })
        cur.close()
        conn.close()
        return render_template('index.html', cuentas=lista_cuentas)
    except Exception as e:
        return f"Error en la base de datos: {e}"

@app.route('/agregar_cuenta', methods=['POST'])
def agregar_cuenta():
    plataforma = request.form['plataforma']
    correo = request.form['correo']
    password = request.form['password']
    vencimiento = request.form['vencimiento']
    
    # IMPORTANTE: Si la fecha viene vacía del HTML, poner None para que SQL no de error
    if vencimiento == '':
        vencimiento = None

    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO cuentas (plataforma, correo, password, vencimiento) VALUES (%s, %s, %s, %s)',
                (plataforma, correo, password, vencimiento))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

# RUTA PARA ELIMINAR (Para que funcione el icono de la basura)
@app.route('/eliminar_cuenta/<int:id>')
def eliminar_cuenta(id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM cuentas WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Configuración necesaria para Render: escucha en el puerto que asigne el sistema
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
>>>>>>> eda12a4ecf8a64bedc3558f6899ee50d9a65dfbb
