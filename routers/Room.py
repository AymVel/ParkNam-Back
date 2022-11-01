
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from db import SessionLocal
from models.Room import Room

router = APIRouter(
    prefix="/room",
    tags=["room"],
    responses={404: {"description": "Not found"}},
)
#Get DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def get_team(db: Session = Depends(get_db)):
    db_team = Room.get_all_room(db)
    if db_team is None:
        raise HTTPException(status_code=404, detail="TeamMember not found")
    return db_team

#Create room
@router.post("/")
async def create_room(number: int, db: Session = Depends(get_db)):
    return Room.create_room(number)


#Delete room
@router.delete('/{id}')
async def delete_team(id: int, db: Session = Depends(get_db)):
    return Room.delete_room(db, id)