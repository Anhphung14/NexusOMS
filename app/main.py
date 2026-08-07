from fastapi import FastAPI
from contextlib import asynccontextmanager

from starlette import status

from app.db.database import create_db_and_tables, test_connection
from app.routers.orders import router as order_router

@asynccontextmanager
async def lifespan(app: FastAPI):
	print("Start application...")
	test_connection()
	create_db_and_tables()
	yield

app = FastAPI(
	lifespan = lifespan,
	title = "FastAPI Application",
	description = "This is a sample FastAPI application.",
	version = "1.0.0",
)

app.include_router(order_router)

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
	return {"message": "Nexus OMS API"}