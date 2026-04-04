import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

def conectar_db():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@app.route('/')
def index():
    conn = conectar_db()
    cur = conn.cursor()
    # Traemos las cuentas ordenadas por fecha de vencimiento
    cur.execute('SELECT id, plataforma, correo, password, vencimiento FROM cuentas ORDER BY vencimiento ASC')
    cuentas_raw = cur.fetchall()
    
    lista_cuentas = []
    hoy = datetime.now().date()
    
    for c in cuentas_raw:
        # Calculamos los días que faltan
        dias_restantes = (c[4] - hoy).days if c[4] else 0
        
        # Traemos los perfiles de esta cuenta específica
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
