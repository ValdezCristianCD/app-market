from flask import redirect, url_for, render_template, request
from models.Market_expenses import Market_expenses
from create_app import create_app, db

app = create_app()

# IMPORTAR LOS MODELOS **después** de crear app, pero **antes** de create_all
with app.app_context():
    from models.Market_expenses import Market_expenses
    db.create_all()

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
        'CARGAR DATA' : '/loadData',
        'MERCADO' : '/market',
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

@app.route('/market')
def market():

    links = {
        'LANDING' : '/landing',
        'CARGAR DATA' : '/loadData',
        'MERCADO' : '/market',
    }

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Mercado Actual' 
    }

    # Solo poblar la base de datos si está vacía
    if Market_expenses.query.count() == 0:
        Market_expenses.population_market_expenses()
        print("Datos cargados.")
    else:
        print("Modelo ya populado.")

    Market_expenses.create_comparation_chart(Market_expenses,'MntMeatProducts','MntFruits')
    
    print(page_vars)

    return render_template('pages/market.html',**page_vars)


@app.route('/upload', methods=['POST'])
def uploadData():
    file = request.files['csv_file']
    if not file.filename.endswith('.csv'):
        return "Archivo inválido", 400

    return redirect('/')




if __name__ == '__main__':
    app.run(debug=True)
