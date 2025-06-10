from flask import Flask, redirect, url_for, render_template, request
from instance.loader_csv import load_csv
from sqlalchemy import create_engine
import os

app = Flask(__name__)

# Asegurar que la carpeta 'instance' exista
os.makedirs(app.instance_path, exist_ok=True)

# Ruta absoluta a la base de datos dentro de /instance
db_path = os.path.join(app.instance_path, 'ifood.db')
engine = create_engine(f'sqlite:///{db_path}')


app_config = {
    'app_name' : 'App Market'
}

@app.route('/')
def index():
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():

    links = {
        'LANDING' : '/landing',
        'CARGAR DATA' : '/loadData'
    }

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Landing' 
    }

    return render_template('pages/landing.html',**page_vars)

@app.route('/loadData')
def loadData():

    links = {
        'LANDING' : '/landing',
        'CARGAR DATA' : '/loadData'
    }

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Cargar Data' 
    }

    return render_template('pages/load_csv.html',**page_vars)


@app.route('/upload', methods=['POST'])
def uploadData():
    file = request.files['csv_file']
    if not file.filename.endswith('.csv'):
        return "Archivo inválido", 400

    df = load_csv(engine, file)

    print(df)

    return redirect('/')

@app.route('/personal', methods=['GET'])
def personal():
    data = db_path.session.query()

    links = {
            'LANDING' : '/landing',
            'CARGAR DATA' : '/loadData'
        }
    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Cargar Data' 
    }
    return render_template('pages/personal.html',**page_vars)

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():

    links = {
            'LANDING' : '/landing',
            'CARGAR DATA' : '/loadData'
        }
    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Cargar Data' 
    }

    if request.method == 'POST':
        people = request.form.get("people")
        income = int(request.form.get("income"))
        if 1 < income < 30000 and people == 1:
            return "Clase Baja (pobre, negro, villero, asqueroso, suciedad, mono, inferior)"
        if 1 < income < 42000 and people == 2:
            return "Clase Baja (pobre, negro, villero, asqueroso, suciedad, mono, inferior)"
        if 1 < income < 60000 and people == 4:
            return "Clase Baja (pobre, negro, villero, asqueroso, suciedad, mono, inferior)"
        if 30000 < income < 40000 and people == 1:
            return "Clase Baja-alta"
        if 42000 < income < 56000 and people == 2:
            return "Clase Baja-alta"
        if 60000 < income < 80000 and people == 4:
            return "Clase Baja-alta"
        if 40000 < income < 55000 and people == 1:
            return "Clase Media-baja"
        if 56000 < income < 78000 and people == 2:
            return "Clase Media-baja"
        if 80000 < income < 110000 and people == 4:
            return "Clase Media-baja"
        if 55000 < income < 90000 and people == 1:
            return "Clase Media"
        if 78000 < income < 127000 and people == 2:
            return "Clase Media"
        if 110000 < income < 180000 and people == 4:
            return "Clase Media"
        if 90000 < income < 130000 and people == 1:
            return "Clase Media-alta"
        if 127000 < income < 183000 and people == 2:
            return "Clase Media-alta"
        if 260000 < income < 400000 and people == 4:
            return "Clase Media-alta"
        if 130000 < income < 200000 and people == 1:
            return "Clase Alta-baja"
        if 183000 < income < 280000 and people == 2:
            return "Clase Alta-baja"
        if 260000 < income < 400000 and people == 4:
            return "Clase Alta-baja"
        if income > 200000 and people == 1:
            return "Clase Alta"
        if income > 280000 and people == 2:
            return "Clase Alta"
        if income > 400000 and people == 4:
            return "Clase Alta"
            
    return render_template('pages/calculator.html',**page_vars)

if __name__ == '__main__':
    app.run(debug=True)

