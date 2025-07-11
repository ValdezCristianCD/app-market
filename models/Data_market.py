import polars as pl
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from create_app import db

class Data_market(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    MntMeatProducts = db.Column(db.Integer)
    Income = db.Column(db.Integer)
    Kidhome = db.Column(db.Integer)
    Teenhome = db.Column(db.Integer)
    Recency = db.Column(db.Integer)
    MntWines = db.Column(db.Integer)
    MntFruits = db.Column(db.Integer)
    MntMeatProducts = db.Column(db.Integer)
    MntFishProducts = db.Column(db.Integer)
    MntSweetProducts = db.Column(db.Integer)
    MntGoldProds = db.Column(db.Integer)
    NumDealsPurchases = db.Column(db.Integer)
    NumWebPurchases = db.Column(db.Integer)
    NumCatalogPurchases = db.Column(db.Integer)
    NumStorePurchases = db.Column(db.Integer)
    NumWebVisitsMonth = db.Column(db.Integer)
    AcceptedCmp3 = db.Column(db.Integer)
    AcceptedCmp4 = db.Column(db.Integer)
    AcceptedCmp5 = db.Column(db.Integer)
    AcceptedCmp1 = db.Column(db.Integer)
    AcceptedCmp2 = db.Column(db.Integer)
    Complain = db.Column(db.Integer)
    Z_CostContact = db.Column(db.Integer)
    Z_Revenue = db.Column(db.Integer)
    Response = db.Column(db.Integer)
    Age = db.Column(db.Integer)
    Customer_Days = db.Column(db.Integer)
    marital_Divorced = db.Column(db.Integer)
    marital_Married = db.Column(db.Integer)
    marital_Single = db.Column(db.Integer)
    marital_Together = db.Column(db.Integer)
    marital_Widow = db.Column(db.Integer)
    education_2n_Cycle = db.Column(db.Integer)
    education_Basic = db.Column(db.Integer)
    education_Graduation = db.Column(db.Integer)
    education_Master = db.Column(db.Integer)
    education_PhD = db.Column(db.Integer)
    MntTotal = db.Column(db.Integer)
    MntRegularProds = db.Column(db.Integer)
    AcceptedCmpOverall = db.Column(db.Integer)

    @classmethod
    def population_from_dataframe(cls, file):
        df = pd.read_csv(file)
        print(df)
        df.columns = df.columns.str.strip()  # Limpieza de columnas
        for _, row in df.iterrows():
            record = cls(
                MntMeatProducts=row.get('MntMeatProducts'),
                Income=row.get('Income'),
                Kidhome=row.get('Kidhome'),
                Teenhome=row.get('Teenhome'),
                Recency=row.get('Recency'),
                MntWines=row.get('MntWines'),
                MntFruits=row.get('MntFruits'),
                MntFishProducts=row.get('MntFishProducts'),
                MntSweetProducts=row.get('MntSweetProducts'),
                MntGoldProds=row.get('MntGoldProds'),
                NumDealsPurchases=row.get('NumDealsPurchases'),
                NumWebPurchases=row.get('NumWebPurchases'),
                NumCatalogPurchases=row.get('NumCatalogPurchases'),
                NumStorePurchases=row.get('NumStorePurchases'),
                NumWebVisitsMonth=row.get('NumWebVisitsMonth'),
                AcceptedCmp3=row.get('AcceptedCmp3'),
                AcceptedCmp4=row.get('AcceptedCmp4'),
                AcceptedCmp5=row.get('AcceptedCmp5'),
                AcceptedCmp1=row.get('AcceptedCmp1'),
                AcceptedCmp2=row.get('AcceptedCmp2'),
                Complain=row.get('Complain'),
                Z_CostContact=row.get('Z_CostContact'),
                Z_Revenue=row.get('Z_Revenue'),
                Response=row.get('Response'),
                Age=row.get('Age'),
                Customer_Days=row.get('Customer_Days'),
                marital_Divorced=row.get('marital_Divorced'),
                marital_Married=row.get('marital_Married'),
                marital_Single=row.get('marital_Single'),
                marital_Together=row.get('marital_Together'),
                marital_Widow=row.get('marital_Widow'),
                education_2n_Cycle=row.get('education_2n_Cycle'),
                education_Basic=row.get('education_Basic'),
                education_Graduation=row.get('education_Graduation'),
                education_Master=row.get('education_Master'),
                education_PhD=row.get('education_PhD'),
                MntTotal=row.get('MntTotal'),
                MntRegularProds=row.get('MntRegularProds'),
                AcceptedCmpOverall=row.get('AcceptedCmpOverall')
            )
            db.session.add(record)
        db.session.commit()

    @classmethod
    def show_table_with_data(cls):
        def as_dict(instance):
            return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
        
        records = cls.query.all()
        return [as_dict(record) for record in records]