import csv
import pickle

import numpy
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.schema import Column
from sqlalchemy import update, desc
from sqlalchemy.types import Integer, Float, String, Boolean, DateTime
from sqlalchemy.sql.expression import func
from db import Base
from scipy import spatial
import datetime
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import pandas as pd



class Place(Base):
    __tablename__ = "Place"
    idplace = Column(Integer, primary_key=True, unique= True, autoincrement=True)
    x = Column(Float)
    y = Column(Float)
    zone = Column(String)
    identifier = Column(Integer)
    month = Column(Integer)
    weekday= Column(Integer)
    hour = Column(Integer)
    minute= Column(Integer)
    disp = Column(Boolean)
    date = Column(DateTime)

    def predict(db: Session, date:datetime):
        data = db.query(Place).group_by(Place.identifier).all()
        data_1 = [[p.identifier,p.zone,1,1] for p in data]
        data_2 = [[p.identifier,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] for p in data]
        training_data = pd.DataFrame(data=data_1,
                                        columns=["IDENTIFIER","ZONE",
                                                 'WEEKDAY_'+str(round(int(date.weekday()) / 2) * 2), 'HOUR_'+str(round(int(date.hour) / 2) * 2)])
        columns = ["IDENTIFIER",
                   'WEEKDAY_0', 'WEEKDAY_1', 'WEEKDAY_2', 'WEEKDAY_3',
                   'WEEKDAY_4', 'WEEKDAY_5', 'WEEKDAY_6', 'HOUR_0', 'HOUR_10', 'HOUR_12',
                   'HOUR_14', 'HOUR_16', 'HOUR_18', 'HOUR_2', 'HOUR_20', 'HOUR_22',
                   'HOUR_4', 'HOUR_6', 'HOUR_8']
        training_data_df = pd.DataFrame(data=data_2,columns=columns)
        training_data_df = training_data_df.merge(training_data.set_index('IDENTIFIER'), on='IDENTIFIER')
        training_data_df = pd.concat([training_data_df, pd.get_dummies(training_data_df[['ZONE']])],
                                     axis=1)
        training_data_df = training_data_df.drop(['ZONE','IDENTIFIER','WEEKDAY_'+str(date.weekday())+'_x', 'HOUR_'+str(date.hour)+'_x'], axis=1)
        cols = training_data_df.columns.tolist()
        cols = cols[-4:] + cols[:-4]
        training_data_df = training_data_df[cols]
        print(training_data_df)
        X = training_data_df.to_numpy()
        loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
        res = loaded_model.predict(X)
        print(res)
        r = []
        for i in range(len(data)):
            if res[i] == '1':
                r.append( (data[i].x, data[i].y))
        print(len(r))
        return Place.toGeoJson(r)
    def train(db:Session):
        with open("training_data.csv", newline='') as f:
            reader = csv.reader(f)
            data = list(reader)


        training_data_df = pd.DataFrame(data=data[1:], columns=data[0])
        training_data_df = training_data_df.rename(
            columns={training_data_df.columns[0]: "ZONE", training_data_df.columns[1]: "LOCALITE"})
        training_data_df = training_data_df.drop(['LOCALITE', 'Geo Point', 'DATETIME', 'MONTH', 'MINUTE'], axis=1)
        training_data_df = pd.concat([training_data_df, pd.get_dummies(training_data_df[['ZONE', 'WEEKDAY', 'HOUR']])],
                                     axis=1).set_index('IDENTIFIANT')
        training_data_df = training_data_df.drop(['ZONE', 'WEEKDAY', 'HOUR'], axis=1)
        print(training_data_df.columns)


        X = training_data_df.drop(['DISPONIBLE'], axis=1).to_numpy()
        y = training_data_df['DISPONIBLE'].to_numpy()
        X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=1)
        clf = MLPClassifier(hidden_layer_sizes=(88, 4), random_state=42, max_iter=2000).fit(X_train, y_train)
        filename = 'finalized_model.sav'
        pickle.dump(clf, open(filename, 'wb'))

        return clf
    def get_all_place(db: Session):
        return db.query(Place).limit(10).all()

    # Create place
    def create_place(db: Session, idplace: int,x:float,y:float,zone:str,identifier:int,month:int,weekday:int,hour:int,minute:int,disp:bool, date:datetime):
        db_place = Place(idplace=idplace, x=x, y=y, zone= zone,identifier=identifier, month=month,weekday=weekday,hour=hour,minute=minute, disp=disp, date=date)
        db.add(db_place)
        db.commit()
        db.refresh(db_place)
        return "ok"

    # Delete place
    def delete_place(db: Session, id):
        team = db.query(Place).filter(Place.idplace == id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        db.delete(team)
        db.commit()
        return {"ok": True}

        # Delete place
    def update_place(db: Session, id,temp, arrived,disp):
            stmt = (
                update(Place).
                    where(Place.idplace == id).values(
                    {'idplace': id, 'arrived': arrived, 'disp': disp,'temp': temp})
            )
            db.execute(stmt)
            db.commit()
            return {"ok": True}
    def closest(db:Session,x:float,y:float):
        l = db.query(Place).group_by(Place.identifier).all()
        l1 = [(place.x,place.y) for place in l]
        tree = spatial.KDTree(l1)
        return l[tree.query([(x, y)])[1][0]]

    def toGeoJson(data:[(float,float)]):
        return {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "parking"}},
            "features": [ { "type": "Feature", "properties": { "id": 1 },
                            "geometry": { "type": "Point", "coordinates": [ d[1],d[0] ] } } for d in data ]}
    def available(db:Session):
        return db.query(Place, func.max(Place.date)).filter(Place.date <= datetime.datetime.now()).group_by(Place.identifier).all()

    def horoadateur(self, x:float,y:float):
        with open('namur-mobilite-horodateurs.csv', newline='') as f:
            reader = csv.reader(f,delimiter=';')
            data = list(reader)
        d = [(i[4].split(',')[0],i[4].split(',')[1]) for i in data[1:]]
        tree = spatial.KDTree(d)
        return d[tree.query([(x, y)])[1][0]]



