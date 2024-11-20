import os
import dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import (
    customer,
    merchant,
    restaurant,
    order,
    admin,
    canteen,
    event,
)


app = FastAPI()

# load the environment variables
dotenv.load_dotenv()

# setup the cors middleware
allow_origins = os.getenv("ALLOW_ORIGINS", "*")
allow_methods = os.getenv("ALLOW_METHODS", "*")
allow_headers = os.getenv("ALLOW_HEADERS", "*")

allow_origins_list = allow_origins.split(",")
allow_methods_list = allow_methods.split(",")
allow_headers_list = allow_headers.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins_list,
    allow_methods=allow_methods_list,
    allow_headers=allow_headers_list,
    allow_credentials=True,
)

app.include_router(customer.router)
app.include_router(merchant.router)
app.include_router(restaurant.router)
app.include_router(canteen.router)
app.include_router(order.router)
app.include_router(event.router)
app.include_router(admin.router)
