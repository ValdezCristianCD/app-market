from flask import redirect, url_for, render_template, request, abort
from models.Market_expenses import Market_expenses
from create_app import create_app, db

app = create_app()

with app.app_context():
    from models.Market_expenses import Market_expenses
    db.create_all()

app_config = {
    'app_name' : 'App Market'
}

links = {
    'LANDING' : '/landing',
    'CARGAR DATA' : '/loadData',
    'MERCADO' : '/market',
}

@app.route('/')
def index():
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Landing' 
    }

    return render_template('pages/landing.html',**page_vars)

@app.route('/loadData')
def loadData():

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Cargar Data' 
    }

    return render_template('pages/load_csv.html',**page_vars)

@app.route('/market')
def market():

    item1 = request.args.get('v1', 'Carne')
    item2 = request.args.get('v2', 'Pescado')

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Mercado Actual' 
    }

    if Market_expenses.query.first() is None:
        Market_expenses.population_market_expenses()

    options = ['Pescado','Carne','Frutas','Dulces','Vinos','Oro']
    page_vars = {
        **page_vars,
        'select_values' : {
            'v1' : {
                'options': options,
                'option_selected' : item1,
            },
            'v2' : {
                'options': options,
                'option_selected' : item2,
            },
        },
    }
    
    try:
        Market_expenses.create_comparation_chart(item1, item2)
    except:
        abort(404)
    
    return render_template('pages/market.html',**page_vars)

@app.route('/info')
def product_info():

    item1 = request.args.get('vid', 'Carne')

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : f'{item1}' 
    }

    try:
        Market_expenses.get_all_data_from_item(item1)
    except:
        abort(404)

    return render_template('pages/product_info.html',**page_vars)

@app.errorhandler(404)
def page_not_found(e):

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Recurso no encontrado',
        'error' : {
            'code': 404,
            'message' : 'Recurso no encontrado',
            'description' : 'Lo sentimos, el recurso solicitado no existe.'
        }
    }

    return render_template('pages/error.html', **page_vars), 404

if __name__ == '__main__':
    app.run(debug=True)


# Set de datos -> Ideas
# Tecnologias -> Todo
# Overview -> Descripcion antes de la muestra, llevarlo a un problema real
# La App -> Modulo por modulo a vender la app y por que cada cosa