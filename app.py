from flask import redirect, url_for, render_template, request, abort, Response
from models.Market_expenses import Market_expenses
from create_app import create_app, db
import matplotlib.pyplot as plt
import io

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
    'ESTADISTICAS' : '/gastos-anuales',
    'CAMPAÑAS': '/grafico_campanias',
    'PERSONAL' : '/perfil-personal',
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

@app.route('/grafico_campanias')
def grafico_campanias():
    Market_expenses.create_all_campaigns_chart()

    page_vars = {
        **app_config,
        'nav_links': links,
        'app_section': 'Gráfico Campañas'
    }

    return render_template('pages/grafico_campanias.html', **page_vars)


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
    limit = request.args.get('limit', 10)

    try:
        response = Market_expenses.get_all_data_from_item(item1, limit)
    except:
        abort(404)

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : f'{item1}',
        'data' : response,
    }

    return render_template('pages/product_info.html',**page_vars)

gastos_data = {
    '2024': { 
        'anual': {
            'Carne': 410,
            'Vino': 58,
            'Frutas': 577,
            'Dulces': 430,
            'Pescado': 144,
            'Oro': 139
        },
        'mensual': {
            'Enero': {'Carne': 35, 'Vino': 5, 'Frutas': 45, 'Dulces': 35, 'Pescado': 12, 'Oro': 0},
            'Febrero': {'Carne': 28, 'Vino': 3, 'Frutas': 38, 'Dulces': 28, 'Pescado': 8, 'Oro': 139},
            'Marzo': {'Carne': 42, 'Vino': 7.50, 'Frutas': 65, 'Dulces': 48, 'Pescado': 18, 'Oro': 0},
            'Abril': {'Carne': 30, 'Vino': 4, 'Frutas': 42, 'Dulces': 32, 'Pescado': 10, 'Oro': 0},
            'Mayo': {'Carne': 38, 'Vino': 6, 'Frutas': 55, 'Dulces': 40, 'Pescado': 15, 'Oro': 0},
            'Junio': {'Carne': 25, 'Vino': 2, 'Frutas': 35, 'Dulces': 25, 'Pescado': 7, 'Oro': 0},
            'Julio': {'Carne': 45, 'Vino': 9, 'Frutas': 75, 'Dulces': 55, 'Pescado': 20, 'Oro': 0},
            'Agosto': {'Carne': 32, 'Vino': 3.50, 'Frutas': 40, 'Dulces': 30, 'Pescado': 9, 'Oro': 0},
            'Septiembre': {'Carne': 40, 'Vino': 7, 'Frutas': 68, 'Dulces': 47, 'Pescado': 17, 'Oro': 0},
            'Octubre': {'Carne': 30, 'Vino': 3, 'Frutas': 43, 'Dulces': 32, 'Pescado': 10, 'Oro': 0},
            'Noviembre': {'Carne': 37, 'Vino': 8, 'Frutas': 60, 'Dulces': 38, 'Pescado': 13, 'Oro': 0},
            'Diciembre': {'Carne': 28, 'Vino': 6, 'Frutas': 31, 'Dulces': 20, 'Pescado': 5, 'Oro': 0},
        }
    },
    '2023': { 
        'anual': {
            'Carne': 635,
            'Vino': 173,
            'Frutas': 426,
            'Dulces': 298,
            'Pescado': 94,
            'Oro': 0
        },
        'mensual': {
            'Enero': {'Carne': 50, 'Vino': 14, 'Frutas': 30, 'Dulces': 25, 'Pescado': 9, 'Oro': 0},
            'Febrero': {'Carne': 48, 'Vino': 10, 'Frutas': 32.50, 'Dulces': 20, 'Pescado': 7, 'Oro': 0},
            'Marzo': {'Carne': 60, 'Vino': 18, 'Frutas': 45, 'Dulces': 30, 'Pescado': 16, 'Oro': 0},
            'Abril': {'Carne': 52, 'Vino': 12, 'Frutas': 35, 'Dulces': 22, 'Pescado': 7, 'Oro': 0},
            'Mayo': {'Carne': 55, 'Vino': 17, 'Frutas': 40, 'Dulces': 28, 'Pescado': 8, 'Oro': 0},
            'Junio': {'Carne': 45, 'Vino': 9, 'Frutas': 28, 'Dulces': 18, 'Pescado': 0, 'Oro': 0},
            'Julio': {'Carne': 70, 'Vino': 20, 'Frutas': 50, 'Dulces': 35, 'Pescado': 9, 'Oro': 0},
            'Agosto': {'Carne': 49, 'Vino': 12, 'Frutas': 33.50, 'Dulces': 21, 'Pescado': 7, 'Oro': 0},
            'Septiembre': {'Carne': 65, 'Vino': 19, 'Frutas': 48, 'Dulces': 32, 'Pescado': 8, 'Oro': 0},
            'Octubre': {'Carne': 50, 'Vino': 10, 'Frutas': 31, 'Dulces': 24, 'Pescado': 7, 'Oro': 0},
            'Noviembre': {'Carne': 58, 'Vino': 16, 'Frutas': 43, 'Dulces': 27, 'Pescado': 9, 'Oro': 0},
            'Diciembre': {'Carne': 33, 'Vino': 17, 'Frutas': 38, 'Dulces': 19, 'Pescado': 8, 'Oro': 0},
        }
    }
}


@app.route('/gastos-anuales')
def mostrar_fluctuacion():
    view_type = request.args.get('type', 'anual')
    year = request.args.get('year', '2024')

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Fluctuación de Gastos Anuales y Mensualeso'
    }

    return render_template(
        'pages/fluctuation.html', 
        **page_vars,
        current_view_type=view_type,
        current_year=year,
        available_years=gastos_data.keys(),
        available_categories=list(gastos_data['2024']['anual'].keys())
    )


@app.route('/plot/gastos')
def plot_gastos():
    view_type = request.args.get('type', 'anual')
    year = request.args.get('year', '2024')
    compare_year = request.args.get('compare_year', None) 
    category = request.args.get('category', None) 
    if year not in gastos_data:
        return "Año no disponible", 404
    if view_type not in ['anual', 'mensual']:
        return "Tipo de vista no válido", 400
    
    data_to_plot = {}
    title = ""
    x_label = ""
    y_label = "Gasto ($)"
    labels = [] 
    fig, ax = plt.subplots(figsize=(12, 7)) 
    if view_type == 'anual':
        if compare_year and compare_year in gastos_data:
            current_year_data = gastos_data[year]['anual']
            compare_year_data = gastos_data[compare_year]['anual']

            categories = sorted(list(set(current_year_data.keys()) | set(compare_year_data.keys())))

            current_values = [current_year_data.get(cat, 0) for cat in categories]
            compare_values = [compare_year_data.get(cat, 0) for cat in categories]

            x = range(len(categories))
            width = 0.35

            ax.bar([i - width/2 for i in x], current_values, width, label=f'Año {year}', color='skyblue')
            ax.bar([i + width/2 for i in x], compare_values, width, label=f'Año {compare_year}', color='lightcoral')

            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45, ha='right')
            ax.legend()
            title = f'Comparación Anual de Gastos: {year} vs {compare_year}'
            x_label = 'Categoría de Gasto'

        else:
            current_year_data = gastos_data[year]['anual']
            categorias = list(current_year_data.keys())
            valores = list(current_year_data.values())
            ax.bar(categorias, valores, color=['skyblue', 'lightcoral', 'lightgreen', 'gold', 'mediumpurple', 'darkgoldenrod'])
            ax.set_xlabel('Categoría de Gasto')
            title = f'Gastos Anuales por Categoría: {year}'
            ax.tick_params(axis='x', rotation=45) 
            plt.tight_layout()

    elif view_type == 'mensual':
        if not category:
            ax.text(0.5, 0.5, 'Selecciona una categoría para ver el desglose mensual.',
                    horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            title = 'Seleccionar Categoría Mensual'
        else:
            if compare_year and compare_year in gastos_data:
                months = list(gastos_data[year]['mensual'].keys()) 
                current_month_values = [gastos_data[year]['mensual'][month].get(category, 0) for month in months]
                compare_month_values = [gastos_data[compare_year]['mensual'][month].get(category, 0) for month in months]

                x = range(len(months))
                width = 0.35

                ax.bar([i - width/2 for i in x], current_month_values, width, label=f'{year} - {category}', color='skyblue')
                ax.bar([i + width/2 for i in x], compare_month_values, width, label=f'{compare_year} - {category}', color='lightcoral')

                ax.set_xticks(x)
                ax.set_xticklabels(months, rotation=45, ha='right')
                ax.legend()
                title = f'Comparación Mensual de Gastos de {category}: {year} vs {compare_year}'
                x_label = 'Mes'
            else:
                months = list(gastos_data[year]['mensual'].keys())
                month_values = [gastos_data[year]['mensual'][month].get(category, 0) for month in months]
                ax.plot(months, month_values, marker='o', linestyle='-', color='skyblue') 
                ax.set_xlabel('Mes')
                title = f'Gastos Mensuales de {category}: {year}'
                ax.tick_params(axis='x', rotation=45) 
                plt.tight_layout()

    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label) 

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close(fig)
    return Response(img_buffer.getvalue(), mimetype='image/png')

@app.route('/perfil-personal') 
def perfil_personal():

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Recurso no encontrado',
        'user_data' : {
            'nombre': 'Martín Pérez',
            'estado_civil': 'Soltero',
            'nivel_educativo': 'Universitario',
            'hijos_pequenos': 1,
            'hijos_adolescentes': 0,
            'ingresos': 250000.00 
        }
    }

    return render_template('pages/personal.html', **page_vars)

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
