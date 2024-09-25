from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import customer, merchant, restaurant, order

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(customer.router)
app.include_router(merchant.router)
app.include_router(restaurant.router)
app.include_router(order.router)
