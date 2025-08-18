from fastapi import FastAPI
from app.routes import comments, tickets, users
from mangum import Mangum

app = FastAPI(title="Ticket System API")

# Include routers for different functionalities
app.include_router(tickets.router)
app.include_router(users.router)
app.include_router(comments.router)

# Create a Mangum handler for AWS Lambda compatibility
handler = Mangum(app)

@app.get("/")
def root():
    return {"message": "API is running"}
