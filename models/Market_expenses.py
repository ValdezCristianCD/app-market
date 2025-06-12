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
    AcceptedCmp1 = db.Column(db.Integer)
    AcceptedCmp2 = db.Column(db.Integer)
    AcceptedCmp3 = db.Column(db.Integer)
    AcceptedCmp4 = db.Column(db.Integer)
    AcceptedCmp5 = db.Column(db.Integer)

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
                AcceptedCmp1 = int(row['AcceptedCmp1']),
                AcceptedCmp2 = int(row['AcceptedCmp2']),
                AcceptedCmp3 = int(row['AcceptedCmp3']),
                AcceptedCmp4 = int(row['AcceptedCmp4']),
                AcceptedCmp5 = int(row['AcceptedCmp5'])
            )
            db.session.add(entry)
        db.session.commit()

    @classmethod
    def create_comparation_chart(cls, item1, item2):
        # Mapeo de nombres legibles a columnas reales
        switch = {
            'Pescado': 'MntFishProducts',
            'Carne': 'MntMeatProducts',
            'Frutas': 'MntFruits',
            'Dulces': 'MntSweetProducts',
            'Vinos': 'MntWines',
            'Oro': 'MntGoldProds',
            'AcceptedCmp1': 'AcceptedCmp1',
            'AcceptedCmp2': 'AcceptedCmp2',
            'AcceptedCmp3': 'AcceptedCmp3',
            'AcceptedCmp4': 'AcceptedCmp4',
            'AcceptedCmp5': 'AcceptedCmp5',
        }

        column_1 = switch.get(item1)
        column_2 = switch.get(item2)

        if not column_1 or not column_2:
            print("Columnas no válidas")
            return

        df = pl.read_csv('./instance/data/ifood_df.csv')
        values_column_1 = df[column_1][:50].to_list()
        values_column_2 = df[column_2][:50].to_list()

        plt.figure(figsize=(8, 6))
        plt.plot(values_column_1, label=item1)
        plt.plot(values_column_2, label=item2)
        plt.title('Comparación de Gastos Entre 2 Áreas')
        plt.legend(loc='upper left')
        plt.ylabel("Gastos")
        plt.xlabel("Últimos 50 registros")
        plt.savefig('./static/img/charts/mtn_prods_chart.png')
        plt.close()

    @classmethod
    def get_all_data_from_item(cls, item1):
        column_1 = cls.get_column_name_by_item_selected(item1)

        if not column_1:
            print("Item no válido")
            return

        df = pl.read_csv('./instance/data/ifood_df.csv')
        values_column = df[column_1][:40].to_list()

        plt.figure(figsize=(8, 6))
        plt.bar(range(len(values_column)), values_column, label=item1)
        plt.title(f'Gastos en {item1}')
        plt.legend(loc='upper left')
        plt.ylabel("Gastos")
        plt.xlabel("Últimos 40 registros")
        plt.savefig('./static/img/charts/mtn_unic_prod_chart.png')
        plt.close()

    @staticmethod
    def get_column_name_by_item_selected(item):
        switch = {
            'Pescado': 'MntFishProducts',
            'Carne': 'MntMeatProducts',
            'Frutas': 'MntFruits',
            'Dulces': 'MntSweetProducts',
            'Vinos': 'MntWines',
            'Oro': 'MntGoldProds',
            'AcceptedCmp1': 'AcceptedCmp1',
            'AcceptedCmp2': 'AcceptedCmp2',
            'AcceptedCmp3': 'AcceptedCmp3',
            'AcceptedCmp4': 'AcceptedCmp4',
            'AcceptedCmp5': 'AcceptedCmp5',
        }
        return switch.get(item)

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
