from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, TIMESTAMP, DATE, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    address = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    cameras = relationship("Camera", back_populates="store")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    name = Column(Text)
    rtsp_url = Column(Text)
    location = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    store = relationship("Store", back_populates="cameras")
    attendance_logs = relationship("AttendanceLog", back_populates="camera")
    environment_logs = relationship("EnvironmentLog", back_populates="camera")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    emp_code = Column(String, unique=True, index=True)
    name = Column(Text)
    role = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    face_embeddings = relationship("FaceEmbedding", back_populates="employee")
    schedules = relationship("Schedule", back_populates="employee")
    attendance_logs = relationship("AttendanceLog", back_populates="employee")


class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    embedding = Column(ARRAY(Float))
    created_at = Column(TIMESTAMP, server_default=func.now())

    employee = relationship("Employee", back_populates="face_embeddings")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(DATE)
    shift_start = Column(TIMESTAMP)
    shift_end = Column(TIMESTAMP)

    employee = relationship("Employee", back_populates="schedules")


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    timestamp = Column(TIMESTAMP, server_default=func.now())
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    confidence = Column(Float)
    snapshot_url = Column(Text)

    employee = relationship("Employee", back_populates="attendance_logs")
    camera = relationship("Camera", back_populates="attendance_logs")


class EnvironmentLog(Base):
    __tablename__ = "environment_logs"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    timestamp = Column(TIMESTAMP, server_default=func.now())
    people_count = Column(Integer)
    brightness = Column(Float)

    camera = relationship("Camera", back_populates="environment_logs")

