from flask import redirect, url_for, render_template, request, abort, Response
from models.Market_expenses import Market_expenses
from create_app import create_app, db
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import random

app = create_app()

with app.app_context():
    from models.Market_expenses import Market_expenses
    db.create_all()

app_config = {
    'app_name' : 'App Market'
}

links = {
    'PERSONAL' : '/perfil-personal',
    'ESTADISTICAS' : '/plot/gastos',
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


def build_plot_image(view_type='anual', category=None):
    item = Market_expenses.query.offset(4).first()  # persona 5

    if not item:
        return None, "No hay datos de la persona 5"

    gastos_base = {
        'Carne': item.MntMeatProducts,
        'Pescado': item.MntFishProducts,
        'Vino': item.MntWines,
        'Frutas': item.MntFruits,
        'Dulces': item.MntSweetProducts,
        'Oro': item.MntGoldProds,
    }

    MULTIPLICADORES = {
        'Carne': (0.8, 1.2),
        'Pescado': (1.4, 0.6),
        'Vino': (1.1, 0.9),
        'Frutas': (0.7, 1.3),
        'Dulces': (1.3, 0.7),
        'Oro': (0.2, 1.8),
    }

    gasto_anio_1 = {k: round(v * MULTIPLICADORES[k][0], 2) for k, v in gastos_base.items()}
    gasto_anio_2 = {k: round(v * MULTIPLICADORES[k][1], 2) for k, v in gastos_base.items()}

    fig, ax = plt.subplots(figsize=(12, 7))
    title = ""
    y_label = "Gasto ($)"
    x_label = ""

    if view_type == 'anual':
        categorias = list(gasto_anio_1.keys())
        valores_1 = [gasto_anio_1[c] for c in categorias]
        valores_2 = [gasto_anio_2[c] for c in categorias]

        x = list(range(len(categorias)))
        width = 0.35

        ax.bar([i - width/2 for i in x], valores_1, width, label='Año Simulado 1', color='skyblue')
        ax.bar([i + width/2 for i in x], valores_2, width, label='Año Simulado 2', color='salmon')
        ax.set_xticks(x)
        ax.set_xticklabels(categorias, rotation=45, ha='right')
        ax.legend()
        title = 'Comparación de Gastos Anuales Simulados'
        x_label = 'Categoría de Gasto'

    elif view_type == 'mensual':
        if not category or category not in gastos_base:
            ax.text(0.5, 0.5, 'Seleccioná una categoría para ver los datos mensuales.',
                    horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            title = 'Seleccionar Categoría Mensual'
        else:
            def dividir_en_meses(total):
                partes = [random.uniform(0.5, 1.5) for _ in range(12)]
                total_partes = sum(partes)
                return [round(total * p / total_partes, 2) for p in partes]

            meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
            valores_1 = dividir_en_meses(gasto_anio_1[category])
            valores_2 = dividir_en_meses(gasto_anio_2[category])

            x = list(range(12))
            ax.plot(x, valores_1, linestyle='-', label='Año Simulado 1', color='skyblue')
            ax.plot(x, valores_2, linestyle='--', label='Año Simulado 2', color='salmon')
            ax.set_xticks(x)
            ax.set_xticklabels(meses, rotation=45)
            ax.legend()
            title = f'Gasto Mensual Simulado en {category}'
            x_label = 'Mes'

    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close(fig)

    return img_buffer, None


@app.route('/plot/gastos')
def plot_gastos():
    view_type = request.args.get('type', 'anual')
    category = request.args.get('category', None)

    img_buffer, error = build_plot_image(view_type, category)
    if error:
        return error, 404

    return Response(img_buffer.getvalue(), mimetype='image/png')

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

@app.route('/perfil-personal') 
def perfil_personal():
    user_data = {
        'nombre': 'Martín Pérez',
        'estado_civil': 'Soltero',
        'nivel_educativo': 'Universitario',
        'hijos_pequenos': 1,
        'hijos_adolescentes': 0,
        'ingresos': 250000.00 
    }
    return render_template('pages/personal.html', user_data=user_data)

if __name__ == '__main__':
    app.run(debug=True)
