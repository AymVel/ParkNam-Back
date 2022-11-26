import csv
import datetime

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException
import httpx
import json
from db import SessionLocal
from models.Place import Place

router = APIRouter(
    prefix="/place",
    tags=["place"],
    responses={404: {"description": "Not found"}},
)
username = "aymvell"
token = "sk.eyJ1IjoiYXltdmVsbCIsImEiOiJjbGFpbmhvNW4wNDh6M3dxdDVueHk5d3pxIn0.GohPgB53ERnd9iB-gtC1iA"
#Get DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def get_place(db: Session = Depends(get_db)):
    db_place = Place.get_all_place(db)
    if db_place is None:
        raise HTTPException(status_code=404, detail="PLace not found")
    return db_place


@router.get("/generate")
async def generate(db: Session = Depends(get_db)):
    with open('training_data.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        # print(data)
    for i in data[1:]:
        Place.create_place(db=db, idplace=None, x=float(i[2].split(',')[0]), y=float(i[2].split(',')[1]),
                           identifier=int(i[3]), zone=i[0], month=int(i[5]),
                           weekday=int(i[6]), hour=int(i[7]),
                           minute=int(i[8]), disp=bool(int(i[9])),
                           date=datetime.datetime.strptime(i[4], '%Y-%m-%d %H:%M:%S'))
    return "ok"
@router.get("/predict/{date}")
async def predict(date: str, db: Session = Depends(get_db)):
    p = Place.predict(db, datetime.datetime.strptime(date, '%Y-%m-%d_%H:%M:%S'))
    return p
@router.get("/train")
async def train( db: Session = Depends(get_db)):
    Place.train(db)
    return "ok"
@router.get("/available")
async def available(db: Session = Depends(get_db)):
    p = Place.available(db)
    l = [(place[0].x, place[0].y) for place in p if place[0].disp]
    print(len(l))
    return Place.toGeoJson(l)

@router.post("/park")
async def take_place(x:str,y:str,stay:str, db: Session = Depends(get_db)):
    date = datetime.datetime.now()
    p = Place.closest(db,float(x),float(y))
    Place.create_place(db=db, idplace=None, x=p.x, y=p.y, identifier=p.identifier, zone=p.zone, month=date.month,
                       weekday=date.day, hour=date.hour,
                       minute=date.minute, disp=False, date = date)
    if stay[-1] == "h":
        departure = date + datetime.timedelta(hours=int(stay[0]))
        Place.create_place(db=db, idplace=None, x=p.x, y=p.y, identifier=p.identifier, zone=p.zone, month=int(departure.month),
                           weekday=int(departure.day), hour=int(departure.hour),
                           minute=int(departure.minute), disp=True, date = date)
        if p.zone == "Bleue" or p.zone == "":
            return ""
        else : return Place.horoadateur(db,p.x,p.y)
    elif stay[-1] == "n":
        departure = date + datetime.timedelta(minutes=30)
        Place.create_place(db=db, idplace=None, x=p.x, y=p.y, identifier=p.identifier, zone=p.zone,
                           month=int(departure.month),
                           weekday=int(departure.day), hour=int(departure.hour),
                           minute=int(departure.minute), disp=True, date = date)
        if p.zone == "Bleue" or p.zone == "":
            return ""
        else : return Place.horoadateur(db,p.x,p.y)
    else :
            if p.zone == "mauve":
                departure = date + datetime.timedelta(minutes=30)
                Place.create_place(db=db, idplace=None, x=p.x, y=p.y, identifier=p.identifier, zone=p.zone,
                                   month=int(departure.month),
                                   weekday=int(departure.day), hour=int(departure.hour),
                                   minute=int(departure.minute), disp=True, date = date)
                return Place.horoadateur(db, p.x, p.y)
            elif p.zone == "rouge":
                departure = date + datetime.timedelta(hours=3)
                Place.create_place(db=db, idplace=None, x=p.x, y=p.y, identifier=p.identifier, zone=p.zone,
                                   month=int(departure.month),
                                   weekday=int(departure.day), hour=int(departure.hour),
                                   minute=int(departure.minute), disp=True, date= date)
                return Place.horoadateur(db, p.x, p.y)
            elif p.zone == "verte":
                departure = date + datetime.timedelta(hours=4)
                Place.create_place(db=db, idplace=None, x=p.x, y=p.y, identifier=p.identifier, zone=p.zone,
                                   month=int(departure.month),
                                   weekday=int(departure.day), hour=int(departure.hour),
                                   minute=int(departure.minute), disp=True, date = date)
                return Place.horoadateur(db, p.x, p.y)
            elif p.zone == "orange":
                departure = date + datetime.timedelta(hours=8)
                Place.create_place(db=db, idplace=None, x=p.x, y=p.y, identifier=p.identifier, zone=p.zone,
                                   month=int(departure.month),
                                   weekday=int(departure.day), hour=int(departure.hour),
                                   minute=int(departure.minute), disp=True, date = date)
                return Place.horoadateur(db,p.x,p.y)
            elif p.zone == "bleue":
                departure = date + datetime.timedelta(hours=3)
                Place.create_place(db=db, idplace=None, x=p.x, y=p.y, identifier=p.identifier, zone=p.zone,
                                   month=int(departure.month),
                                   weekday=int(departure.day), hour=int(departure.hour),
                                   minute=int(departure.minute), disp=True, date = date)
                return ""
            else:
                departure = date + datetime.timedelta(hours=3)
                Place.create_place(db=db, idplace=None, x=p.x, y=p.y, identifier=p.identifier, zone=p.zone,
                                   month=int(departure.month),
                                   weekday=int(departure.day), hour=int(departure.hour),
                                   minute=int(departure.minute), disp=True, date=date)
                return ""

