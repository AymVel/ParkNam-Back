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

    def predict(db: Session, date:datetime,duration:str):
        w = round(int(date.weekday()) / 2) * 2
        if w == 24:
            w = 0
        weekday = str(w)
        h = round(int(date.hour) / 2) * 2
        if h == 24:
            h = 0
        hour = str(h)
        data = db.query(Place).group_by(Place.identifier).all()
        data_1 = [[p.x,p.y,p.identifier,p.zone,1,1] for p in data]
        data_2 = [[p.identifier,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] for p in data]
        training_data = pd.DataFrame(data=data_1,
                                        columns=["X","Y","IDENTIFIER","ZONE",
                                                 'WEEKDAY_'+weekday, 'HOUR_'+hour])
        columns = ["IDENTIFIER",
                   'WEEKDAY_0', 'WEEKDAY_1', 'WEEKDAY_2', 'WEEKDAY_3',
                   'WEEKDAY_4', 'WEEKDAY_5', 'WEEKDAY_6', 'HOUR_0', 'HOUR_10', 'HOUR_12',
                   'HOUR_14', 'HOUR_16', 'HOUR_18', 'HOUR_2', 'HOUR_20', 'HOUR_22',
                   'HOUR_4', 'HOUR_6', 'HOUR_8']
        training_data_df = pd.DataFrame(data=data_2,columns=columns)
        res = training_data_df.merge(training_data.set_index('IDENTIFIER'), on='IDENTIFIER')
        training_data_df = pd.concat([res, pd.get_dummies(res[['ZONE']])],axis=1)
        training_data_df = training_data_df.drop(['X','Y','ZONE','IDENTIFIER','WEEKDAY_'+weekday+'_x', 'HOUR_'+hour+'_x'], axis=1)

        training_data_df = training_data_df.rename(columns = {'WEEKDAY_'+weekday+'_y':'WEEKDAY_'+weekday,'HOUR_'+hour+'_y':'HOUR_'+hour})
        c = [19,20,21,22,23]
        for i in range(17):
            if i == int(weekday):
                c.append(17)
            c.append(i)
        if h == 0:
            c.insert( 12, 18)
        elif h == 10:
            c.insert( 13, 18)
        elif h == 12:
            c.insert(14, 18)
        elif h == 14:
            c.insert(15, 18)
        elif h == 16:
            c.insert(16, 18)
        elif h == 18:
            c.insert(17, 18)
        elif h == 2:
            c.insert(18, 18)
        elif h == 20:
            c.insert( 19, 18)
        elif h == 22:
            c.insert( 20, 18)
        elif h == 4:
            c.insert( 21, 18)
        elif h == 6:
            c.insert( 22, 18)
        training_data_df = training_data_df.iloc[:,c]
        print(training_data_df.columns)
        X = training_data_df.to_numpy()
        loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
        res['prediction'] = loaded_model.predict(X)
        print(res[res['prediction'] == '1'])
        if duration[-1] == "n":
            l = [(place[20], place[21]) for place in res.values.tolist() if place[25]=='1']
        elif duration[-1] == "h":
            if duration[0] == "3":
                l = [(place[20], place[21]) for place in res.values.tolist() if
                     place[25] == '1' and (place[22] == "Rouge" or place[22] == "Bleue" or place[22] == "Verte" or place[22] == "Orange")]
            elif duration[0] == "4":
                l = [(place[20], place[21]) for place in res.values.tolist() if
                     place[25] == '1' and (place[22] == "Verte" or place[22] == "Orange")]
            elif duration[0] == "8":
                l = [(place[20], place[21]) for place in res.values.tolist() if
                     place[25] == '1' and place[22] == "Orange"]

        return Place.toGeoJson(l)
    def train(db:Session):
        with open("training_data.csv", newline='') as f:
            reader = csv.reader(f)
            data = list(reader)


        training_data_df = pd.DataFrame(data=data[1:], columns=data[0])
        training_data_df = training_data_df.rename(
            columns={training_data_df.columns[0]: "ZONE", training_data_df.columns[1]: "LOCALITE"})
        training_data_df = training_data_df.drop(['LOCALITE', 'Geo Point', 'DATETIME', 'MONTH', 'MINUTE'], axis=1)
        training_data_df = pd.concat([training_data_df, pd.get_dummies(training_data_df[['ZONE','WEEKDAY', 'HOUR']])],
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



