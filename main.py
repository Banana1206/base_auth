from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.responses import RedirectResponse
from app.endpoints import user_endpoint
from app.core.auth import get_current_user
from app.db import init_database, close_database
import uvicorn

# Create FastAPI instance
app = FastAPI()

# Database events
@app.on_event("startup")
async def on_startup():
    """Initialize the database connection."""
    init_database()

@app.on_event("shutdown")
async def on_shutdown():
    """Close the database connection."""
    close_database()

# Include user routes
app.include_router(user_endpoint.router, tags=['Users'], prefix='/api/users')

# Redirect to docs page
@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')

# Optionally, add global authentication dependency if needed for all routes
# app = FastAPI(dependencies=[Depends(get_current_user)])

# Run the application with uvicorn if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
