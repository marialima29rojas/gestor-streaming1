import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_por_defecto")

DB_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_8dhJvITgMB4j@ep-muddy-sky-agpgcsus-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require")

def conectar_db():
    return psycopg2.connect(DB_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plataforma/<nombre>')
def ver_plataforma(nombre):
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute('SELECT id, correo, password FROM cuentas WHERE plataforma = %s ORDER BY id ASC', (nombre,))
        cuentas_raw = cur.fetchall()
        
        hoy = datetime.now().date()
        lista_cuentas = []
        
        for c in cuentas_raw:
            cur.execute('''
                SELECT nombre_usuario, pin, contacto, id, vencimiento 
                FROM perfiles 
                WHERE id_cuenta = %s 
                ORDER BY id ASC
            ''', (c[0],))
            
            perfiles_raw = cur.fetchall()
            perfiles_procesados = []
            
            for p in perfiles_raw:
                vencimiento = p[4] # p[4] es la fecha de vencimiento
                dias_restantes = None
                
                if vencimiento:
                    # Calculamos la resta de fechas
                    delta = vencimiento - hoy
                    dias_restantes = delta.days
                
                perfiles_procesados.append({
                    'nombre': p[0],
                    'pin': p[1],
                    'contacto': p[2],
                    'id': p[3],
                    'vencimiento': vencimiento,
                    'dias_restantes': dias_restantes
                })
            
            lista_cuentas.append({
                'id': c[0], 
                'correo': c[1], 
                'password': c[2], 
                'perfiles': perfiles_procesados
            })
            
        cur.close()
        return render_template('plataforma.html', nombre=nombre, cuentas=lista_cuentas, hoy=hoy)
    except Exception as e:
        return f"Error: {e}"
    finally:
        if conn: conn.close()

# --- LAS DEMÁS RUTAS (agregar_cuenta, eliminar, etc.) SE MANTIENEN IGUAL ---

@app.route('/nueva_cuenta/<plat>')
def vista_form_cuenta(plat):
    return render_template('form_cuenta.html', nombre=plat)

@app.route('/agregar_cuenta', methods=['POST'])
def agregar_cuenta():
    plat = request.form['plat_nombre']
    id_cuenta = request.form.get('id')
    correo = request.form['correo']
    password = request.form['password']
    conn = conectar_db()
    cur = conn.cursor()
    if id_cuenta:
        cur.execute('UPDATE cuentas SET correo=%s, password=%s WHERE id=%s', (correo, password, id_cuenta))
    else:
        cur.execute('INSERT INTO cuentas (plataforma, correo, password) VALUES (%s, %s, %s)', (plat, correo, password))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('ver_plataforma', nombre=plat))

@app.route('/nuevo_perfil/<plat>')
def vista_form_perfil(plat):
    id_seleccionada = request.args.get('id_cuenta')
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT id, correo FROM cuentas WHERE plataforma = %s ORDER BY id ASC', (plat,))
    cuentas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('form_perfil.html', nombre=plat, cuentas=cuentas, id_seleccionada=id_seleccionada)

@app.route('/agregar_perfil', methods=['POST'])
def agregar_perfil():
    plat = request.form['plat_nombre']
    id_perfil = request.form.get('id')
    vencimiento = request.form.get('vencimiento') 
    conn = conectar_db()
    cur = conn.cursor()
    if not vencimiento: vencimiento = None
    if id_perfil:
        cur.execute('UPDATE perfiles SET id_cuenta=%s, nombre_usuario=%s, pin=%s, contacto=%s, vencimiento=%s WHERE id=%s',
                    (request.form['id_cuenta'], request.form['nombre'], request.form['pin'], request.form['contacto'], vencimiento, id_perfil))
    else:
        cur.execute('INSERT INTO perfiles (id_cuenta, nombre_usuario, pin, contacto, vencimiento) VALUES (%s, %s, %s, %s, %s)',
                    (request.form['id_cuenta'], request.form['nombre'], request.form['pin'], request.form['contacto'], vencimiento))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('ver_plataforma', nombre=plat))

@app.route('/editar_cuenta/<int:id>/<plat>')
def vista_editar_cuenta(id, plat):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT id, correo, password FROM cuentas WHERE id = %s', (id,))
    cuenta = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('form_cuenta.html', nombre=plat, cuenta=cuenta, edit=True)

@app.route('/eliminar_cuenta/<int:id>/<plat>')
def eliminar_cuenta(id, plat):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM cuentas WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('ver_plataforma', nombre=plat))

@app.route('/editar_perfil/<int:id>/<plat>')
def vista_editar_perfil(id, plat):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT id, nombre_usuario, pin, contacto, id_cuenta, vencimiento FROM perfiles WHERE id = %s', (id,))
    perfil = cur.fetchone()
    cur.execute('SELECT id, correo FROM cuentas WHERE plataforma = %s ORDER BY id ASC', (plat,))
    cuentas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('form_perfil.html', nombre=plat, perfil=perfil, cuentas=cuentas, edit=True)

@app.route('/eliminar_perfil/<int:id>/<plat>')
def eliminar_perfil(id, plat):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM perfiles WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('ver_plataforma', nombre=plat))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)