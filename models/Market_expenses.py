import polars as pl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from create_app import db

class Market_expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    MntMeatProducts = db.Column(db.Integer)
    MntFruits = db.Column(db.Integer)
    MntFishProducts = db.Column(db.Integer)
    MntSweetProducts = db.Column(db.Integer)
    MntWines = db.Column(db.Integer)
    MntGoldProds = db.Column(db.Integer)

    @classmethod
    def population_market_expenses(cls):
        df = pl.read_csv('./instance/data/ifood_df.csv')

        for row in df.iter_rows(named=True):
            entry = cls(
                MntMeatProducts = int(row['MntMeatProducts']) * 10,
                MntFruits = int(row['MntFruits']) * 10,
                MntFishProducts = int(row['MntFishProducts']) * 10,
                MntSweetProducts = int(row['MntSweetProducts']) * 10,
                MntWines = int(row['MntWines']) * 10,
                MntGoldProds = int(row['MntGoldProds']) * 10,
            )
            db.session.add(entry)
        db.session.commit()

    @classmethod
    def create_comparation_chart(cls, item1, item2):
        # Mapeo de nombres legibles a columnas reales
        column_1 = cls.get_column_name_by_item_selected(item1)
        column_2 = cls.get_column_name_by_item_selected(item2)

        values_column_1 = []
        values_column_2 = []

        data = cls.query.limit(50).all()
        for row in data:
            values_column_1.append(getattr(row, column_1))
            values_column_2.append(getattr(row, column_2))

        plt.figure(figsize=(8,6))

        plt.plot(values_column_1, label=item1)
        plt.plot(values_column_2, label=item2)

        plt.title('Comparacion de Gastos Entre 2 Areas')
        plt.legend(loc='upper left')
        plt.ylabel("Gastos en Dolares")
        plt.xlabel("Ultimos 50 Gastos") 
        plt.savefig('./static/img/charts/mtn_prods_chart.png')
        plt.close()

    @classmethod
    def get_all_data_from_item(cls, item1, limit):
        column_1 = cls.get_column_name_by_item_selected(item1)

        values_column = []

        data = db.session.query(cls).with_entities(getattr(cls, column_1)).limit(limit).all()

        for value in data:
            values_column.append(value[0])

        plt.figure(figsize=(8,6))

        plt.bar(list(range(0,limit)), label=item1, height=values_column)

        plt.title(f'Analisis de {item1}')
        plt.legend(loc='upper left')
        plt.ylabel("Gastos en Dolares")
        plt.xlabel(f'Ultimos {limit} Gastos') 
        plt.savefig('./static/img/charts/mtn_unic_prod_chart.png')
        plt.close()

        average_value = sum(values_column) / len(values_column)
        max_expense = max(values_column)
        min_expense = min(values_column)

        return {'Valor Promedio' : average_value, 'Valor Maximo' : max_expense, 'Valor Minimo' : min_expense} 

    @staticmethod
    def get_column_name_by_item_selected(item):
        switch = {
            'Pescado': 'MntFishProducts',
            'Carne': 'MntMeatProducts',
            'Frutas': 'MntFruits',
            'Dulces': 'MntSweetProducts',
            'Vinos': 'MntWines',
            'Oro': 'MntGoldProds',
        }
        return switch.get(item)

    #Mas adelante, Se debe crear otro modelo especifico para las campañas 
    @classmethod
    def create_all_campaigns_chart(cls):
        df = pl.read_csv('./instance/data/ifood_df.csv')

        total_cmp = {
            'Cmp1': df['AcceptedCmp1'].sum(),
            'Cmp2': df['AcceptedCmp2'].sum(),
            'Cmp3': df['AcceptedCmp3'].sum(),
            'Cmp4': df['AcceptedCmp4'].sum(),
            'Cmp5': df['AcceptedCmp5'].sum(),
        }

        plt.figure(figsize=(8, 6))
        plt.bar(total_cmp.keys(), total_cmp.values(), color='skyblue')
        plt.title('Cantidad de Clientes que Aceptaron cada Campaña')
        plt.ylabel('Cantidad de Aceptaciones')
        plt.xlabel('Campañas')
        plt.savefig('./static/img/charts/campaigns_chart.png')
        plt.close()

        return  {'Campaña 1': df['AcceptedCmp1'].sum(), 'Campaña 2': df['AcceptedCmp2'].sum(), 'Campaña 3': df['AcceptedCmp3'].sum(), 'Campaña 4': df['AcceptedCmp4'].sum(), 'Campaña 5': df['AcceptedCmp5'].sum()}