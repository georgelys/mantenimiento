from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, IntegerField,  StringField, EmailField, PasswordField, SelectField, TextAreaField, validators 
from passlib.hash import sha256_crypt
from functools import wraps
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'mantenimiento'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER'] = 'static'

mysql = MySQL(app)

Download_PATH = 'pdf'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
Download_FOLDER = os.path.join(APP_ROOT, Download_PATH)

def esta_logeado(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Usted no inicio sesion', 'danger')
            return redirect(url_for('login'))
    return wrap

def es_dir(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['rol'] == 'Director':
            return f(*args, **kwargs)
        else:
            flash('Usted no tiene autorizacion para esta accion', 'danger')
            return redirect(url_for('index'))
    return wrap

def es_biom(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['rol'] == 'Biomedico':
            return f(*args, **kwargs)
        else:
            flash('Usted no tiene autorizacion para esta accion', 'danger')
            return redirect(url_for('index'))
    return wrap

def es_bioq(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['rol'] == 'Bioquimico':
            return f(*args, **kwargs)
        else:
            flash('Usted no tiene autorizacion para esta accion', 'danger')
            return redirect(url_for('index'))
    return wrap

def es_sup(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['rol'] == 'Director' or session['rol'] == 'Biomedico':
            return f(*args, **kwargs)
        else:
            flash('Usted no tiene autorizacion para esta accion', 'danger')
            return redirect(url_for('index'))
    return wrap
###
def buscarequipos(search):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipos WHERE descripcion LIKE %s OR marca LIKE %s OR modelo LIKE %s OR servicio LIKE %s OR origen LIKE %s",
                (search, search, search, search, search))
    res = cur.fetchall()
    cur.close()
    return results

# def getcalmes(equipments):
    calmes = [
        {
            0: 'Mes',
            1: 'Enero',
            2: 'Febrero',
            3: 'Marzo',
            4: 'Abril',
            5: 'Mayo',
            6: 'Junio',
            7: 'Julio',
            8: 'Agosto',
            9: 'Septiembre',
            10: 'Octubre',
            11: 'Noviembre',
            12: 'Diciembre'
        }
    ]
    for equipment in equipments:
        if equipment['category'] == 'I':
            eqmonth = equipment['dati'].month
            if equipment['frequency'] == 'A':
                ite = {}
                ite[0] = equipment['description']
                i = 1
                while i <= 12:
                    ite[i] = ''
                    i = i + 1
                ite[eqmonth] = 'X'
            else:
                if equipment['frequency'] == 'S':
                    if eqmonth + 6 <= 12:
                        ite = {}
                        ite[0] = equipment['description']
                        i = 1
                        while i <= 12:
                            ite[i] = ''
                            i = i + 1
                        ite[eqmonth] = 'X'
                        ite[eqmonth+6] = 'X'
                    else:
                        ite = {}
                        ite[0] = equipment['description']
                        i = 1
                        while i <= 12:
                            ite[i] = ''
                            i = i + 1
                        ite[eqmonth] = 'X'
                        ite[eqmonth-6] = 'X'
                else:
                    x = eqmonth
                    while x > 4:
                        x = x - 3
                    ite = {}
                    ite[0] = equipment['description']
                    i = 1
                    while i <= 12:
                        ite[i] = ''
                        i = i + 1
                    ite[x] = 'X'
                    ite[x+3] = 'X'
                    ite[x+6] = 'X'
                    ite[x+9] = 'X'
                    # equipment['mema'] = x, x+3, x+6, x+9
            calmes.append(ite)
    return calmes


###

class UsuarioForm(Form):
    rol = SelectField('Rol', choices=[
        ('Biomedico', 'Biomedico'),
        ('Bioquimico', 'Bioquimico')
    ])
    area = SelectField('Area', choices=[
        ('', 'Seleccione el area'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C')
    ])
    nombre = StringField('Nombre', [
        validators.Length(min=1, max=50),
        validators.DataRequired()
    ])
    username = StringField('Nombre de usuario', [
        validators.Length(min=4, max=25), 
        validators.DataRequired()
    ])
    password = PasswordField('Contraseña', [
        validators.DataRequired(),
        validators.EqualTo('confirmpass', message='Las contraseñas no coinciden')
    ])
    confirmpass = PasswordField('Confirmar contraseña')

class ObsForm(Form):
    titulo = StringField('Titulo', [validators.Length(min=1, max=200)])
    obs = TextAreaField('Observacion', [validators.Length(min=15)])

class RepEquipoForm(Form):
    titulo = StringField('Titulo', [validators.Length(min=1, max=200)])
    reporte = TextAreaField('Reporte de equipo', [validators.Length(min=15)])

class RepInsumoForm(Form):
    titulo = StringField('Titulo', [validators.Length(min=1, max=200)])
    reporte = TextAreaField('Reporte de insumos', [validators.Length(min=15)])

@app.route('/hacer_obs', methods=['GET', 'POST'])
@es_bioq
def hacer_obs():
    form = ObsForm(request.form)
    if request.method == 'POST' and form.validate():
        titulo = form.titulo.data
        obs = form.obs.data

        cur = mysql.connection.cursor()
        cur. execute('INSERT INTO observaciones(titulo, obs, usuario) VALUES(%s, %s, %s)', (titulo, obs, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('Observacion enviada', 'success')

        return redirect(url_for('index'))
    
    return render_template('hacer_obs.html', form=form)

@app.route('/obs')
@es_sup
def observaciones():
    cur = mysql.connection.cursor()
    res = cur.execute('SELECT * FROM observaciones')
    observaciones = cur.fetchall()
    cur.close()
    
    if res > 0:
        return render_template('obs.html', observaciones=observaciones)
    else:
        msg = 'No hay observaciones'
        return render_template('obs.html', msg=msg)

@app.route('/obs/<string:id>/')
@es_sup
def observacion(id):
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM observaciones WHERE id = %s", [id])
    observacion = cur.fetchone()

    return render_template('obsone.html', observacion=observacion)

@app.route('/eli_obs/<string:id>/')
@es_sup
def eli_obs(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM observaciones WHERE id = %s', [id])
    mysql.connection.commit()
    cur.close()
    
    flash('Observacion eliminada', 'success')
    return redirect(url_for('index'))

@app.route('/repequipo', methods=['GET', 'POST'])
@es_biom
def hacer_repequipo():
    form = RepEquipoForm(request.form)
    if request.method == 'POST' and form.validate():
        titulo = form.titulo.data
        reporte = form.reporte.data

        cur = mysql.connection.cursor()
        cur. execute('INSERT INTO repequipos(titulo, reporte, usuario) VALUES(%s, %s, %s)', (titulo, reporte, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('Reporte de equipo enviado', 'success')

        return redirect(url_for('index'))
    
    return render_template('repequipo.html', form=form)

@app.route('/repequipos')
@es_dir
def repequipos():
    cur = mysql.connection.cursor()
    res = cur.execute('SELECT * FROM repequipos')
    repequipos = cur.fetchall()
    cur.close()
    
    if res > 0:
        return render_template('repequipos.html', repequipos=repequipos)
    else:
        msg = 'No hay reportes de equipos'
        return render_template('repequipos.html', msg=msg)

@app.route('/repequipo/<string:id>/')
@es_dir
def repequipo(id):
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM repequipos WHERE id = %s", [id])
    repequipo = cur.fetchone()

    return render_template('repequipoone.html', repequipo=repequipo)

@app.route('/eli_repequipo/<string:id>/')
@es_dir
def eli_repequipo(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM repequipos WHERE id = %s', [id])
    mysql.connection.commit()
    cur.close()
    
    flash('Reporte de equipo eliminado', 'success')
    return redirect(url_for('index'))

@app.route('/repinsumo', methods=['GET', 'POST'])
@es_bioq
def hacer_repinsumo():
    form = RepInsumoForm(request.form)
    if request.method == 'POST' and form.validate():
        titulo = form.titulo.data
        reporte = form.reporte.data

        cur = mysql.connection.cursor()
        cur. execute('INSERT INTO repinsumos(titulo, reporte, usuario) VALUES(%s, %s, %s)', (titulo, reporte, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('Reporte de insumo enviado', 'success')

        return redirect(url_for('index'))
    
    return render_template('repinsumo.html', form=form)

@app.route('/repinsumos')
@es_dir
def repinsumos():
    cur = mysql.connection.cursor()
    res = cur.execute('SELECT * FROM repinsumos')
    repinsumos = cur.fetchall()
    cur.close()
    
    if res > 0:
        return render_template('repinsumos.html', repinsumos=repinsumos)
    else:
        msg = 'No hay reportes de insumos'
        return render_template('repinsumos.html', msg=msg)

@app.route('/repinsumo/<string:id>/')
@es_dir
def repinsumo(id):
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM repinsumos WHERE id = %s", [id])
    repinsumo = cur.fetchone()

    return render_template('repinsumoone.html', repinsumo=repinsumo)

@app.route('/eli_repinsumo/<string:id>/')
@es_dir
def eli_repinsumo(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM repinsumos WHERE id = %s', [id])
    mysql.connection.commit()
    cur.close()
    
    flash('Reporte de insumo eliminado', 'success')
    return redirect(url_for('index'))

@app.route('/equipos', methods=['GET', 'POST'])
@esta_logeado
def equipos():
    if request.method == 'POST':
        data = dict(request.form)
        if data["search"] != '':
            equipos = buscarequipos(data["search"])
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM equipos")
            equipos = cur.fetchall()
            cur.close()
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM equipos")
        equipos = cur.fetchall()
        cur.close()
    if equipos:
        return render_template('equipos.html', equipos=equipos)
    else:
        flash('No se encontraron equipos', 'warning')
        return render_template('equipos.html')


@app.route('/')
@esta_logeado
def index():
    return render_template('index.html')

@app.route('/usuarios')
@es_dir
def usuarios():
    cur = mysql.connection.cursor()
    res = cur.execute('SELECT * FROM usuarios WHERE rol != "Director"')
    usuarios = cur.fetchall()
    cur.close()
    
    if res > 0:
        return render_template('usuarios.html', usuarios=usuarios)
    else:
        msg = 'No hay personal registrado'
        return render_template('usuarios.html', msg=msg)

@app.route('/usuario/<string:id>/', methods=['GET', 'POST'])
@es_dir
def editar_usuario(id):
    cur = mysql.connection.cursor()
    res = cur.execute('SELECT * FROM usuarios WHERE id = %s', [id])
    usuario = cur.fetchone()
    cur.close()

    form = UsuarioForm(request.form)
    form.rol.data = usuario['rol']
    form.area.data = usuario['area']
    form.nombre.data = usuario['nombre']
    form.username.data = usuario['username']

    if request.method == 'POST' and form.validate:
        rol = request.form['rol']
        if rol == 'Biomedico':
            area = ''
        else:
            area = request.form['area']
        nombre = request.form['nombre']
        username = request.form['username']
        password = sha256_crypt.encrypt(str(request.form['password']))

        cur = mysql.connection.cursor()
        cur.execute('UPDATE usuarios SET rol=%s, area=%s, nombre=%s, username=%s, password=%s WHERE id=%s', (rol, area, nombre, username, password, id))
        mysql.connection.commit()
        cur.close()

        flash('Usuario actualizado', 'success')
        return redirect(url_for('index'))

    return render_template('regusuario.html', form=form)

@app.route('/usuario/regusuario', methods=['GET', 'POST'])
@es_dir
def regusuario():
    error = None
    form = UsuarioForm(request.form)
    if(request.method == 'POST' and form.validate):
        rol = form.rol.data
        if rol == 'Biomedico':
            area = ''
        else:
            area = form.area.data
        nombre = form.nombre.data
        username =form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios(area, rol, nombre, username, password) VALUES(%s, %s, %s, %s, %s)", (area, rol, nombre, username, password))
        mysql.connection.commit()
        cur.close()

        flash('Ah registrado el usuario', 'success')

        return redirect(url_for('index'))

    return render_template('regusuario.html', form=form)

@app.route('/eli_usuario/<string:id>/', methods=['POST'])
@es_dir
def eli_usuario(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM usuarios WHERE id = %s', [id])
    mysql.connection.commit()
    cur.close()
    
    flash('Usuario eliminado', 'success')
    return redirect(url_for('index'))

@app.route('/iusuario', methods=['GET', 'POST'])
def login():
    error = None
    if 'logged_in' in session:
        error = 'Usted ya inicio sesion'
        return render_template('index.html', error=error)
    else:
        if request.method == 'POST':
            username = request.form['username']
            password_ingresada = request.form['password']

            cur = mysql.connection.cursor()
            result = cur.execute("SELECT * FROM usuarios WHERE username = %s", [username])
            if result > 0:
                data = cur.fetchone()
                password = data['password']
                if sha256_crypt.verify(password_ingresada, password):
                    session['logged_in'] = True
                    session['username'] = username
                    session['rol'] = data['rol']
                    # ssession['rol'] = data['rol']

                    flash('Usted inicio sesion correctamente', 'success')
                    return redirect(url_for('index'))
                else:
                    error = 'Nombre de usuario o contraseña incorrectos'
                    return render_template('iusuario.html', error=error)
            else:
                error = 'Nombre de usuario o contraseña incorrectos'
                return render_template('iusuario.html', error=error)
        return render_template('iusuario.html')

@app.route('/logout')
@esta_logeado
def logout():
    session.clear()
    flash('Se desconecto su sesion', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key='fldsmdfr'
    app.run(debug=True)