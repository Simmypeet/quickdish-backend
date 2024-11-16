from logging import error
import logging
import jwt
from api.errors import ConflictingError, NotFoundError

from api.errors import ConflictingError, NotFoundError
from api.errors.authentication import AuthenticationError
from api.schemas.authentication import AuthenticationResponse
from api.state import REFRESH_TOKEN_EXPIRE_DAYS, REFRESH_TOKEN_EXPIRE_SECOND, State
from api.models.customer import Customer, CustomerReview
from api.models.RefreshToken import RefreshToken
from api.schemas.customer import (
    CustomerLogin,
    CustomerRegister,
    CustomerReview as CustomerReviewSchema,
    CustomerReviewCreate,
    CustomerUpdate
)
from fastapi.responses import JSONResponse

from typing import List
import hashlib
from fastapi import HTTPException, Request, Response

# import datetime
from datetime import datetime, timedelta, timezone


async def register_customer(
    state: State, customer_create: CustomerRegister, response: Response
) -> AuthenticationResponse:
    """Create a new customer in the database."""
    try: 
        # Check if a customer with the same username or email already exists
        
        existing_customer = (
            state.session.query(Customer)
            .filter(
                (Customer.username == customer_create.username)
                | (Customer.email == customer_create.email),
            )
            .first()
        )

        if existing_customer:
            raise ConflictingError(
                "an account with the same username or email already exists"
            )

        salt, hashed_password = state.generate_password(customer_create.password)

        new_customer = Customer(
            first_name=customer_create.first_name,
            last_name=customer_create.last_name,
            username=customer_create.username,
            email=customer_create.email,
            hashed_password=hashed_password,
            salt=salt,
        )

        state.session.add(new_customer)
        state.session.commit()

        state.session.refresh(new_customer)

        token = state.encode_jwt(
            {"customer_id": new_customer.id}
        )

        refresh_token = state.create_refresh_token(
            {"customer_id": new_customer.id}
        )

        #store refresh token in database 
        stored_refresh_token = RefreshToken(
            customer_id = new_customer.id,
            role = "user",  
            token = refresh_token,
            expired_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            # expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECOND)
        )
        #add refresh token to database if not exists, if already exists, update the token
        state.session.add(stored_refresh_token)
        state.session.commit()

        #set refresh token in HTTP-only cookie
        # response.set_cookie(
        #     key="refresh_token",
        #     value=refresh_token,
        #     httponly=True,
        #     secure=True,
        #     samesite="lax",
        #     max_age=timedelta(REFRESH_TOKEN_EXPIRE_DAYS),
        # )
        response.delete_cookie(
            "refresh_token"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=False,
            secure=False,
            samesite="lax",
            max_age=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            # max_age = timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECOND)
        )
        
        role = "user"
        return AuthenticationResponse(
            role=role, jwt_token=token, id=new_customer.id  # type: ignore
        )
    except Exception as e:
        logging.error("Error registering customer: %s", e)
        raise AuthenticationError("error registering customer")


async def login_customer(
    state: State, customer_login: CustomerLogin, response: Response
) -> AuthenticationResponse:
    """Authenticate a customer and return a JWT token."""
    try: 
        customer = (
            state.session.query(Customer)
            .filter(Customer.username == customer_login.username)
            .first()
        )

        if not customer:
            raise AuthenticationError("invalid username or password")

        salted_password = customer_login.password + customer.salt
        hashsed_password = hashlib.sha256(salted_password.encode()).hexdigest()

        if hashsed_password != customer.hashed_password:
            raise AuthenticationError("invalid username or password")

        token = state.encode_jwt({"customer_id": customer.id})
        refresh_token = state.create_refresh_token(
            {"customer_id": customer.id}
        )

        #store refresh token in database 
        add_or_update_refresh_token(state, "user", customer.id, refresh_token)
        
        #work
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=False, #type HTTP-only cookie
            secure=False, #change to True in production: works only on HTTPS
            samesite="lax", #Strict = cross-site cookies are not sent on cross-site requests, Lax = cookies are sent on top-level navigations and will be sent along with GET requests initiated by third party website
            max_age= timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            # max_age = timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECOND)
        )
        print("New refresh token set in cookie:", refresh_token)

        
        role = "user"

        return AuthenticationResponse(
            role=role, jwt_token=token, id=customer.id  # type: ignore
        )
    except Exception as e:
        logging.error("Error logging in customer: %s", e)
        raise AuthenticationError("invalid username or password")

async def refresh_access_token(state: State, request: Request) -> AuthenticationResponse:
    try: 
        # print("refresh token: ", response)
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token missing")

        refresh_token_pair = state.session.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        customer_id = refresh_token_pair.customer_id
        customer = state.session.query(Customer).filter(Customer.id == customer_id).first()

        if not customer:
            raise HTTPException(status_code=402, detail="Invalid token")

        if refresh_token_pair.expired_at < datetime.now():
            raise HTTPException(status_code=405, detail="Token expired")
            #problem : frontend should handle this like redirect to login page, if backend return exception 
        
        try:
            payload = state.encode_jwt({"customer_id": customer_id})
            return AuthenticationResponse( role="user", jwt_token=payload, id=customer_id)
            # raise HTTPException(status_code=405, detail="Token expired")

        except error as e: 
            logging.error("Error encoding JWT: %s", e)

        return AuthenticationResponse(
            role="Invalid", jwt_token="Invalid", id=customer_id
        )
    except Exception as e:
        logging.error("Error refreshing token: %s", e)

def add_or_update_refresh_token(state: State, role: str, customer_id: int, refresh_token: str) -> None:
    existing_refresh_token = state.session.query(RefreshToken).filter(RefreshToken.customer_id == customer_id).first()
    if existing_refresh_token: 
        existing_refresh_token.token = refresh_token
        existing_refresh_token.expired_at = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        # existing_refresh_token.expired_at = datetime.now() + timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECOND)

    else: 
        new_refresh_token = RefreshToken(
            customer_id = customer_id,
            role = role,
            token = refresh_token,
            expired_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            # expired_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECOND)

        )
        state.session.add(new_refresh_token)

    try: 
        state.session.commit()

    except Exception as e:
        state.session.rollback()
        logging.error("Error adding or updating refresh token: %s", e)


async def get_customer(state: State, customer_id: int) -> Customer:
    """Get a customer by their ID."""
    try: 
        result = (
            state.session.query(Customer)
            .filter(Customer.id == customer_id)
            .first()
        )

        if result is None:
            raise NotFoundError("customer with the ID in the token is not found")

        return result
    except Exception as e: 
        logging.error("Error getting customer: %s", e)


async def update_customer(state: State, customer_id: int, payload: CustomerUpdate): 
    logging.info("received customer ", payload)
    result = (
        state.session.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if compare_password(state, payload.password, result.salt, result.hashed_password): 
        result.username = payload.username
        result.email = payload.email
        if payload.new_password != '':
            salt, new_hashed_password = state.generate_password(payload.new_password)
            result.hashed_password = new_hashed_password  
            result.salt = salt
            state.session.commit()
            return JSONResponse(
                status_code=200,
                content={"message": "Customer updated successfully"},
            )

        if result is None: 
            raise NotFoundError("customer with the ID in the token is not found")
    else: 
        raise HTTPException(status_code=402, detail="Unmatched password")
  


def compare_password(state: State, str_pw: str, salt: str, hashed_pw: str) -> bool:
    """Compare a plain password with a hashed password. -> true = same"""
    salted_str_pw = str_pw + salt
    hashed_str_pw = hashlib.sha256(salted_str_pw.encode()).hexdigest()
    return hashed_pw == hashed_str_pw
        



# customer review
async def get_customer_reviews(
    state: State, customer_id: int
) -> List[CustomerReviewSchema]:
    """Get a customer's reviews by their ID."""
    results = (
        state.session.query(CustomerReview)
        .filter(CustomerReview.customer_id == customer_id)
        .all()
    )  # result = list of sql alchemy model so needed to be converted to list of pydantic model

    return [CustomerReviewSchema.model_validate(review) for review in results]


async def create_customer_review(
    state: State, customerID: int, reviewDetail: CustomerReviewCreate
) -> int:
    sql_review = CustomerReview(
        customer_id=customerID,
        restaurant_id=reviewDetail.restaurant_id,
        menu_id=reviewDetail.menu_id,
        review=reviewDetail.review,
        tastiness=reviewDetail.tastiness,
        hygiene=reviewDetail.hygiene,
        quickness=reviewDetail.quickness,
        created_at=datetime.now(),
    )
    state.session.add(sql_review)
    state.session.flush()
    state.session.commit()

    return sql_review.id
