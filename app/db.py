import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# URL de conexión a sqlite
DATABASE_URL = os.getenv("DATABASE_URL")


# Motor de conexión con la db
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#Obtener una sesión de la db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Prueba de conexión
def probar_conexion():
    try:
        connection = engine.connect()
        print("Conexión exitosa")
        connection.close()
    except OperationalError:
        print("Error al conectarse")

probar_conexion()
