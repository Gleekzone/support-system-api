from fastapi import FastAPI
from mangum import Mangum
from sqlalchemy.exc import OperationalError
from app.routes import tickets, users
from common.db import Base, engine
from common.logger import logger 
from app.dependencies.auth import CognitoClient
from app.schemas.user import LoginRequest

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


auth_client = CognitoClient() 

@app.post("/login")
async def login(data: LoginRequest):
    logger.info(f"Login attempt for user: {data.username}")
    tokens = auth_client.authenticate(data.username, data.password)
    return tokens


# Root endpoint to check if the API is running
@app.get("/")
def root():
    return {"message": "API is running"}

# Create a Mangum handler for AWS Lambda compatibility
handler = Mangum(app)
