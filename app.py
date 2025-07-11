from flask import redirect, url_for, render_template, request, abort, Response
from models.Market_expenses import Market_expenses
from models.Data_market import Data_market
from create_app import create_app, db
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, os, math
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
    'ESTADISTICAS' : '/fluctuacion',
    'CAMPAÑAS': '/grafico_campanias',
    'PERSONAL' : '/perfil-personal',
    'CALCULADORA' : '/calculator',
    'DATOS' : 'view_data?age_min=&age_max=&income_min=&income_max=&marital_status=&education=',
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
    item = Market_expenses.query.offset(4).first()

    if not item:
        return None, None, "No hay datos de la persona 5"

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


    if view_type == 'mensual':
        fig, ax = plt.subplots()
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
            ax.plot(x, valores_1, linestyle='-', label='2023', color='skyblue')
            ax.plot(x, valores_2, linestyle='--', label='2024', color='salmon')
            ax.set_xticks(x)
            ax.set_xticklabels(meses, rotation=45)
            ax.legend()
            title = f'Gasto Mensual en {category}'
            x_label = 'Mes'
        x_label = 'Mes'
        ax.set_title(title)
        ax.set_ylabel('Gastos ($USD)')
        ax.set_xlabel(x_label)
        plt.tight_layout()

        filename = f"plot_{view_type}_{category}_{random.randint(1000,9999)}.png"
        filename_real = os.path.join('static', 'img', filename)
        plt.savefig(filename_real)
        plt.close(fig)

        return filename, None, None

    gasto_anio_3 = {}
    gasto_anio_4 = {}

    for cat in gastos_base:
        x1, y1 = 2023, gasto_anio_1[cat]
        x2, y2 = 2024, gasto_anio_2[cat]
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1

        gasto_anio_3[cat] = round(min(5000, max(0, m * 2025 + b)), 2)
        gasto_anio_4[cat] = round(min(5000, max(0, m * 2026 + b)), 2)

    categorias = list(gasto_anio_1.keys())
    x = list(range(len(categorias)))
    width = 0.35

    # === Gráfico real ===
    fig1, ax1 = plt.subplots(figsize=(12, 7))
    ax1.bar([i - width/2 for i in x], [gasto_anio_1[c] for c in categorias], width, label='2023', color='skyblue')
    ax1.bar([i + width/2 for i in x], [gasto_anio_2[c] for c in categorias], width, label='2024', color='salmon')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categorias, rotation=45, ha='right')
    ax1.legend()
    ax1.set_title('Gastos Anuales Reales')
    ax1.set_ylabel('Gasto ($)')
    ax1.set_xlabel('Categoría de Gasto')
    plt.tight_layout()
    filename_real = f"plot_real_{random.randint(1000,9999)}.png"
    filepath_real = os.path.join('static', 'img', filename_real)
    plt.savefig(filepath_real)
    plt.close(fig1)

    # === Gráfico predicción ===
    fig2, ax2 = plt.subplots(figsize=(12, 7))
    ax2.bar([i - width/2 for i in x], [gasto_anio_3[c] for c in categorias], width, label='2025 (pred)', color='lightgreen', alpha=0.8)
    ax2.bar([i + width/2 for i in x], [gasto_anio_4[c] for c in categorias], width, label='2026 (pred)', color='orange', alpha=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(categorias, rotation=45, ha='right')
    ax2.legend()
    ax2.set_title('Predicción de Gastos Anuales')
    ax2.set_ylabel('Gasto ($)')
    ax2.set_xlabel('Categoría de Gasto')
    plt.tight_layout()
    filename_pred = f"plot_pred_{random.randint(1000,9999)}.png"
    filepath_pred = os.path.join('static', 'img', filename_pred)
    plt.savefig(filepath_pred)
    plt.close(fig2)

    
    return filename_real, filename_pred, None

@app.route('/fluctuacion')
def mostrar_fluctuacion():
    view_type = request.args.get('type', 'anual')
    category = request.args.get('category')
    year = request.args.get('year', '2023')

    available_years = ['2023']
    available_categories = ['Carne', 'Pescado', 'Vino', 'Frutas', 'Dulces', 'Oro']

    filename_real, filename_pred, error = build_plot_image(view_type, category)
    if error:
        return error, 404

    page_vars = {
        **app_config,
        'nav_links': links,
        'app_section': 'Fluctuación',
        'img_path_real': url_for('static', filename=f'img/{filename_real}'),
        'img_path_pred': url_for('static', filename=f'img/{filename_pred}'),
        'available_years': available_years,
        'available_categories': available_categories,
        'current_year': year,
        'current_view_type': view_type
    }

    return render_template('pages/fluctuation.html', **page_vars)

@app.route('/perfil-personal') 
def perfil_personal():

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Perfil',
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
    page = request.args.get('page', 1, type=int)
    per_page = 50

    age_min = request.args.get('age_min', type=int)
    age_max = request.args.get('age_max', type=int)
    income_min = request.args.get('income_min', type=int)
    income_max = request.args.get('income_max', type=int)
    marital_status = request.args.get('marital_status')
    education = request.args.get('education')

    query = Data_market.query

    if age_min is not None:
        query = query.filter(Data_market.Age >= age_min)
    if age_max is not None:
        query = query.filter(Data_market.Age <= age_max)
    if income_min is not None:
        query = query.filter(Data_market.Income >= income_min)
    if income_max is not None:
        query = query.filter(Data_market.Income <= income_max)

    if marital_status:
        query = query.filter(getattr(Data_market, f"marital_{marital_status}") == 1)
    if education:
        query = query.filter(getattr(Data_market, f"education_{education}") == 1)

    pagination = query.paginate(page=page, per_page=per_page)
    data = pagination.items

    page_vars = {
        **app_config,
        'nav_links': links,
        'app_section': 'Ver Datos',
        'data': data,
        'columns': [column.name for column in Data_market.__table__.columns],
        'pagination': pagination,
        'filters': {
            'age_min': age_min,
            'age_max': age_max,
            'income_min': income_min,
            'income_max': income_max,
            'marital_status': marital_status,
            'education': education
        }
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

