import logging

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.calculation_factory import CalculationFactory
from app.crud import (
    create_calculation,
    create_user,
    get_calculation,
    get_user_by_email,
    get_user_by_username,
)
from app.database import Base, engine, get_db
from app.models import Calculation, User
from app.operations import add, divide, multiply, subtract
from app.schemas import (
    CalculationCreate,
    CalculationRead,
    UserCreate,
    UserRead,
)
from app.security import verify_password


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI Secure Users Calculator")

# Create SQLAlchemy tables that do not already exist.
Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator("a", "b")
    @classmethod
    def validate_numbers(cls, value: float) -> float:
        if not isinstance(value, (int, float)):
            raise ValueError("Both a and b must be numbers.")

        return value


class OperationResponse(BaseModel):
    result: float = Field(
        ...,
        description="The result of the operation",
    )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")


class UserLogin(BaseModel):
    username: str
    password: str


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    logger.error(
        "HTTP exception on %s: %s",
        request.url.path,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    error_messages = "; ".join(
        f"{error['loc'][-1]}: {error['msg']}"
        for error in exc.errors()
    )

    logger.error(
        "Validation error on %s: %s",
        request.url.path,
        error_messages,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": error_messages},
    )


@app.get("/")
async def read_root(request: Request):
    """Serve the calculator webpage."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the application health status for Docker."""
    return {"status": "healthy"}


# --------------------------------------------------
# User routes
# --------------------------------------------------


@app.post(
    "/users/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """Create a user while storing only the password hash."""
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    try:
        user = create_user(db, user_data)
        logger.info("Created user: %s", user.username)
        return user

    except IntegrityError as error:
        db.rollback()
        logger.error("Database integrity error: %s", error)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        ) from error


@app.post(
    "/users/login",
    response_model=UserRead,
)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db),
) -> User:
    """Verify a user's username and password."""
    user = get_user_by_username(
        db,
        login_data.username,
    )

    if user is None or not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    logger.info("User logged in: %s", user.username)
    return user


@app.get(
    "/users/{username}",
    response_model=UserRead,
)
def read_user(
    username: str,
    db: Session = Depends(get_db),
) -> User:
    """Retrieve a user without returning the password hash."""
    user = get_user_by_username(db, username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# --------------------------------------------------
# Calculation BREAD routes
# --------------------------------------------------


@app.post(
    "/calculations",
    response_model=CalculationRead,
    status_code=status.HTTP_201_CREATED,
)
def add_calculation(
    calculation_data: CalculationCreate,
    db: Session = Depends(get_db),
) -> Calculation:
    """Add a calculation and store it in the database."""
    user = db.get(User, calculation_data.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        calculation = create_calculation(
            db,
            calculation_data,
        )

        logger.info(
            "Created calculation %s for user %s",
            calculation.id,
            calculation.user_id,
        )

        return calculation

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except IntegrityError as error:
        db.rollback()
        logger.error("Calculation database error: %s", error)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create calculation",
        ) from error


@app.get(
    "/calculations",
    response_model=list[CalculationRead],
)
def browse_calculations(
    db: Session = Depends(get_db),
) -> list[Calculation]:
    """Browse all calculations stored in the database."""
    statement = select(Calculation).order_by(
        Calculation.id.asc()
    )

    return list(db.scalars(statement).all())


@app.get(
    "/calculations/{calculation_id}",
    response_model=CalculationRead,
)
def read_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
) -> Calculation:
    """Read one calculation by its ID."""
    calculation = get_calculation(
        db,
        calculation_id,
    )

    if calculation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    return calculation


@app.put(
    "/calculations/{calculation_id}",
    response_model=CalculationRead,
)
def edit_calculation(
    calculation_id: int,
    calculation_data: CalculationCreate,
    db: Session = Depends(get_db),
) -> Calculation:
    """Edit an existing calculation and recalculate its result."""
    calculation = get_calculation(
        db,
        calculation_id,
    )

    if calculation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    user = db.get(User, calculation_data.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        operation = CalculationFactory.create(
            calculation_data.type,
        )

        result = operation.calculate(
            calculation_data.a,
            calculation_data.b,
        )

        calculation.a = calculation_data.a
        calculation.b = calculation_data.b
        calculation.type = calculation_data.type.value
        calculation.result = result
        calculation.user_id = calculation_data.user_id

        db.commit()
        db.refresh(calculation)

        logger.info(
            "Updated calculation: %s",
            calculation.id,
        )

        return calculation

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except IntegrityError as error:
        db.rollback()
        logger.error("Calculation update error: %s", error)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update calculation",
        ) from error


@app.delete(
    "/calculations/{calculation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Delete a calculation from the database."""
    calculation = get_calculation(
        db,
        calculation_id,
    )

    if calculation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    db.delete(calculation)
    db.commit()

    logger.info(
        "Deleted calculation: %s",
        calculation_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# --------------------------------------------------
# Original arithmetic routes
# --------------------------------------------------


@app.post(
    "/add",
    response_model=OperationResponse,
    responses={400: {"model": ErrorResponse}},
)
async def add_route(
    operation: OperationRequest,
) -> OperationResponse:
    try:
        return OperationResponse(
            result=add(operation.a, operation.b),
        )

    except Exception as error:
        logger.error("Add operation error: %s", error)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@app.post(
    "/subtract",
    response_model=OperationResponse,
    responses={400: {"model": ErrorResponse}},
)
async def subtract_route(
    operation: OperationRequest,
) -> OperationResponse:
    try:
        return OperationResponse(
            result=subtract(operation.a, operation.b),
        )

    except Exception as error:
        logger.error("Subtract operation error: %s", error)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@app.post(
    "/multiply",
    response_model=OperationResponse,
    responses={400: {"model": ErrorResponse}},
)
async def multiply_route(
    operation: OperationRequest,
) -> OperationResponse:
    try:
        return OperationResponse(
            result=multiply(operation.a, operation.b),
        )

    except Exception as error:
        logger.error("Multiply operation error: %s", error)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@app.post(
    "/divide",
    response_model=OperationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def divide_route(
    operation: OperationRequest,
) -> OperationResponse:
    try:
        return OperationResponse(
            result=divide(operation.a, operation.b),
        )

    except ValueError as error:
        logger.error("Divide operation error: %s", error)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Unexpected division error: %s",
            error,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from error


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )