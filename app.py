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




if __name__ == '__main__':
    app.run(debug=True)
