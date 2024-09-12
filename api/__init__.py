from fastapi import FastAPI
from api.routers import customer, merchant, restaurant

app = FastAPI()

app.include_router(customer.router)
app.include_router(merchant.router)
app.include_router(restaurant.router)
