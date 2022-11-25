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
        data_x = [[x.x, x.y, x.identifier, date.month, date.day, date.hour, date.minute] for x in data]
        loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
        p = numpy.array(data_x)
        res = loaded_model.predict(p)
        print(res)
        r = []
        for i in range(len(data_x)):
            if res[i]:
                r.append( (data_x[i][0], data_x[i][1]))
        print(len(r))
        return Place.toGeoJson(r)
    def train(db:Session):
        training_data = db.query(Place).all()
        training_data_x = [[x.x,x.y,x.identifier,x.month,x.weekday,x.hour,x.minute] for x in training_data]
        training_data_y = [y.disp for y in training_data]
        X = numpy.array(training_data_x)
        y = numpy.array(training_data_y)
        X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=1)
        clf = MLPClassifier(random_state=42, max_iter=2000, hidden_layer_sizes= (88, 4)).fit(X_train, y_train)
        filename = 'finalized_model.sav'
        pickle.dump(clf, open(filename, 'wb'))
        return clf
    # Get All places
    def get_all_place(db: Session):
        return db.query(Place).all()

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
        l = db.query(Place).all()
        l1 = [(place.x,place.y) for place in l]
        tree = spatial.KDTree(l1)
        return l[tree.query([(x, y)])[1][0]]

    def toGeoJson(data:[(float,float)]):
        return {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "parking"}},
            "features": [ { "type": "Feature", "properties": { "id": 1 },
                            "geometry": { "type": "Point", "coordinates": [ d[0],d[1] ] } } for d in data ]}
    def available(db:Session):
        return db.query(Place, func.max(Place.date)).filter(Place.date <= datetime.datetime.now()).group_by(Place.identifier).all()

    def horoadateur(self, x:float,y:float):
        with open('namur-mobilite-horodateurs.csv', newline='') as f:
            reader = csv.reader(f,delimiter=';')
            data = list(reader)
        d = [(i[4].split(',')[0],i[4].split(',')[1]) for i in data[1:]]
        tree = spatial.KDTree(d)
        return d[tree.query([(x, y)])[1][0]]



