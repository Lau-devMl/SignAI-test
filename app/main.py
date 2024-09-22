from fastapi import FastAPI
from .db import engine
from .models import Base

# Creación de tablas 
Base.metadata.create_all(bind=engine)

app = FastAPI()


