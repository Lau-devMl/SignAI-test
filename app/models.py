from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Date
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime

# Tabla de usuarios
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)  
    nombre_usuario = Column(String(255), unique=True, nullable=False) 
    contraseña = Column(String(255), nullable=False)  
    correo = Column(String(255), unique=True, nullable=False)  

    datos_cargados = relationship("DatoCargado", back_populates="usuario")

# Tabla de datos cargados
class DatoCargado(Base):
    __tablename__ = "datos_cargados"
    
    id_datos = Column(Integer, primary_key=True, index=True) 
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))  
    nombre_archivo = Column(String(255), nullable=False) 
    fecha_carga = Column(Date, default=datetime.utcnow)  
    atributo = Column(String(255), nullable=False)  
    etiqueta = Column(String(255), nullable=True)  
    valor = Column(Float, nullable=False) 
    categoria = Column(String(255), nullable=True)  
    resultado = Column(Boolean, nullable=True)  

    usuario = relationship("Usuario", back_populates="datos_cargados")
