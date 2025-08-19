from fastapi import FastAPI
from mangum import Mangum
from sqlalchemy.exc import OperationalError
from app.routes import tickets, users
from common.db import Base, engine
from common.logger import logger 


app = FastAPI(title="Ticket System API",
              docs_url="/docs")

# Try to create tables safely
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully")
except OperationalError as e:
    logger.warning(f"Could not connect to DB: {e}")

# Include routers for different functionalities
app.include_router(tickets.router)
app.include_router(users.router)

# Root endpoint to check if the API is running
@app.get("/")
def root():
    return {"message": "API is running"}

# Create a Mangum handler for AWS Lambda compatibility
handler = Mangum(app)
