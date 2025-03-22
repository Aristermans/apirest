from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los dominios (puedes restringirlo)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

# URL de conexión a PostgreSQL en Railway
DATABASE_URL = "postgresql://postgres:YHwsefcnMtsNzrbulFAVunTfEfxjjAFY@mainline.proxy.rlwy.net:23902/railway"

# Configuración de SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo Pydantic para viajes
class Viaje(BaseModel):
    id: int
    destino: str
    fecha: str
    precio: float

# Ruta para obtener todos los viajes
@app.get("/viajes")
def get_viajes(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM viajes"))
    viajes = result.fetchall()
    return [dict(row._mapping) for row in viajes]  # Convierte a JSON

# Ruta para obtener un solo viaje por ID
@app.get("/viajes/{viaje_id}")
def get_viaje(viaje_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM viajes WHERE id = :id"), {"id": viaje_id})
    viaje = result.fetchone()
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return dict(viaje._mapping)

# Ruta para eliminar un viaje por ID
@app.delete("/viajes/{viaje_id}")
def delete_viaje(viaje_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("DELETE FROM viajes WHERE id = :id RETURNING id"), {"id": viaje_id})
    db.commit()
    if not result.rowcount:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return {"message": "Viaje eliminado"}
