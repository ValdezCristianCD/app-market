from flask import redirect, url_for, render_template, request, abort, Response
from models.Market_expenses import Market_expenses
from models.Data_market import Data_market
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
    'LANDING' : '/landing',
    'CARGAR DATA' : '/loadData',
    'MERCADO' : '/market',
    'ESTADISTICAS' : '/plot/gastos',
    'CAMPAÑAS': '/grafico_campanias',
    'PERSONAL' : '/perfil-personal',
    'CALCULADORA' : '/calculator'
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
    data = Market_expenses.create_all_campaigns_chart()

    page_vars = {
        **app_config,
        'nav_links': links,
        'app_section': 'Gráfico Campañas',
        'data' : data
    }

    return render_template('pages/grafico_campanias.html', **page_vars)


@app.route('/loadData', methods=['GET','POST'])
def upload_market_csv():

    file = request.files.get('csv_file')
    if file:
        Data_market.population_from_dataframe(file)
        return redirect(url_for('view_loaded_data'))
        
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

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():

    links = {
        'LANDING' : '/landing',
        'CARGAR DATA' : '/loadData',
        'MERCADO' : '/market',
        'ESTADISTICAS' : '/plot/gastos',
        'CAMPAÑAS': '/grafico_campanias',
        'PERSONAL' : '/perfil-personal',
        'CALCULADORA' : '/calculator'
        }
    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Calculadora de clases' 
    }

    if request.method == 'POST':
        people = int(request.form.get("people"))
        
        income = int(request.form.get("income"))
        print(income)
        def class_calculator():
            if 1 < income < 30000 and people == 1:
                return "Usted pertenece a la Clase Baja, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 1 < income < 42000 and people == 2:
                return "Usted pertenece a la Clase Baja, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 1 < income < 60000 and people == 4:
                return "Usted pertenece a la Clase Baja, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 30000 < income < 40000 and people == 1:
                return "Usted pertenece a la Clase Baja-alta, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 42000 < income < 56000 and people == 2:
                return "Usted pertenece a la Clase Baja-alta, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 60000 < income < 80000 and people == 4:
                return "Usted pertenece a la Clase Baja-alta, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 40000 < income < 55000 and people == 1:
                return "Usted pertenece a la Clase Media-baja, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 56000 < income < 78000 and people == 2:
                return "Usted pertenece a la Clase Media-baja, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 80000 < income < 110000 and people == 4:
                return "Usted pertenece a la Clase Media-baja, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 55000 < income < 90000 and people == 1:
                return "Usted pertenece a la Clase Media, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 78000 < income < 127000 and people == 2:
                return "Usted pertenece a la Clase Media, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 110000 < income < 180000 and people == 4:
                return "Usted pertenece a la Clase Media, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 90000 < income < 130000 and people == 1:
                return "Usted pertenece a la Clase Media-alta, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 127000 < income < 183000 and people == 2:
                return "Usted pertenece a la Clase Media-alta, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 260000 < income < 400000 and people == 4:
                return "Usted pertenece a la Clase Media-alta, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 130000 < income < 200000 and people == 1:
                return "Usted pertenece a la Clase Alta-baja, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 183000 < income < 280000 and people == 2:
                return "Usted pertenece a la Clase Alta-baja, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if 260000 < income < 400000 and people == 4:
                return "Usted pertenece a la Clase Alta-baja, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if income > 200000 and people == 1:
                return "Usted pertenece a la Clase Alta, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if income > 280000 and people == 2:
                return "Usted pertenece a la Clase Alta, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
            if income > 400000 and people == 4:
                return "Usted pertenece a la Clase Alta, esto es solo un estimado teniendo en cuenta los datos ingresados sobre las personas en su hogar y sus ingresos."
        page_vars["display_data"] = class_calculator()  
        
    return render_template('pages/calculator.html',**page_vars)
@app.route('/view_data', methods=['GET'])
def view_loaded_data():
    data = Data_market.query.limit(500).all()

    page_vars = {
        **app_config,
        'nav_links': links,
        'app_section': 'Ver Datos',
        'data': data,
        'columns': [column.name for column in Data_market.__table__.columns]
    }

    return render_template('pages/view_data.html', **page_vars)


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

