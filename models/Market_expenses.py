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
                MntMeatProducts = int(row['MntMeatProducts']),
                MntFruits = int(row['MntFruits']),
                MntFishProducts = int(row['MntFishProducts']),
                MntSweetProducts = int(row['MntSweetProducts']),
                MntWines = int(row['MntWines']),
                MntGoldProds = int(row['MntGoldProds'])
            )
            db.session.add(entry)

        db.session.commit()
        print("Base de datos populada con éxito usando Polars.")

    def create_comparation_chart(cls, item1, item2):

        values_item1 = []
        values_item2 = []

        data = cls.query.all()
        for row in data[:50]:
            values_item1.append(getattr(row, item1))
            values_item2.append(getattr(row, item2))

        plt.figure(figsize=(8,6))

        plt.plot(values_item1, label=item1)
        plt.plot(values_item2, label=item2)

        plt.title('Other')
        plt.legend(loc='lower left')
        plt.savefig('./static/img/charts/mtn_prods_chart.png')
        plt.close()
