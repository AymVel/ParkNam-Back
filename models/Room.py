from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Float
from db import Base



class Room(Base):
    __tablename__ = "Room"
    idroom = Column(Integer, primary_key=True, unique= True, autoincrement=True)
    temperature = Column(Float)

    # Get All rooms
    def get_all_room(db: Session):
        return db.query(Room).all()

    # Create room
    def create_room(db: Session, number: Integer):
        for i in range(number):
            db_room = Room(temperature= 0)
            db.add(db_room)
            db.commit()
            db.refresh(db_room)
        return str(number) + " room added"

    # Delete room
    def delete_room(db: Session, id):
        team = db.query(Room).filter(Room.idroom == id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        db.delete(team)
        db.commit()
        return {"ok": True}
