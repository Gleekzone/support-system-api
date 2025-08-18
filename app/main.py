from fastapi import FastAPI
from mangum import Mangum
from app.routes import comments, tickets, users
from common.db import Base, engine


app = FastAPI(title="Ticket System API")

Base.metadata.create_all(bind=engine)

# Include routers for different functionalities
app.include_router(tickets.router)
app.include_router(users.router)
app.include_router(comments.router)

# Root endpoint to check if the API is running
@app.get("/")
def root():
    return {"message": "API is running"}

# Create a Mangum handler for AWS Lambda compatibility
handler = Mangum(app)
