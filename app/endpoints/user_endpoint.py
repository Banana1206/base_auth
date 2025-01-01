from fastapi import APIRouter, Response, status, HTTPException, Depends
from datetime import datetime, timedelta
from app.models.user_schema import CreateUserSchema, LoginUserSchema, UserBaseSchema
from app.db import User
from app.core.auth import get_current_user, get_hashed_password, verify_password, create_access_token, create_refresh_token
from config import settings
from app.serializers.data_serialize import to_entity
from app.models.response_schema import ResponseModel

router = APIRouter()


# [...] register user
@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
async def create_user(payload: CreateUserSchema):
    # Check if user already exist
    user = User.find_one({'email': payload.email.lower()})
    if user:
        return ResponseModel(
            status= False,
            message= " Account already exist"
        )
    # Compare password and passwordConfirm
    if payload.password != payload.passwordConfirm:
        return ResponseModel(
            status= False,
            message= "Passwords do not match."
        )
    #  Hash the password
    payload.password = get_hashed_password(payload.password)
    del payload.passwordConfirm
    payload.role = 'user'
    payload.verified = True
    payload.email = payload.email.lower()
    payload.created_at = datetime.utcnow()
    payload.updated_at = payload.created_at
    result = User.insert_one(payload.dict())
    if not result.acknowledged:
        return ResponseModel(
            status=False,
            message="Could not insert user to db."
        )
    new_user = to_entity(User.find_one({'_id': result.inserted_id}))
    return ResponseModel(
        status= True,
        data=new_user,
        message="Operation successful."
    )


# [...] login user
@router.post('/login')
def login(payload: LoginUserSchema, response: Response):
    # Check if the user exist
    db_user = User.find_one({'email': payload.email.lower()})
    if not db_user:
        return ResponseModel(
            status= False,
            message= "Incorrect Email."
        )
        
    user = to_entity(db_user)

    # Check if the password is valid
    if not verify_password(payload.password, user['password']):
        return ResponseModel(
            status= False,
            message= "Incorrect Password."
        )

    # Create access token
    access_token = create_access_token(
        subject=str(user["email"]), expires_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN))

    # Create refresh token
    refresh_token = create_refresh_token(
        subject=str(user["email"]), expires_time=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_IN))

    # Store refresh and access tokens in cookie
    response.set_cookie('access_token', access_token, settings.ACCESS_TOKEN_EXPIRES_IN,
                        settings.ACCESS_TOKEN_EXPIRES_IN, '/', None, False, True, 'lax')
    response.set_cookie('refresh_token', refresh_token,
                        settings.REFRESH_TOKEN_EXPIRES_IN, settings.REFRESH_TOKEN_EXPIRES_IN, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', settings.ACCESS_TOKEN_EXPIRES_IN,
                        settings.ACCESS_TOKEN_EXPIRES_IN, '/', None, False, False, 'lax')

    # Send both access
    return ResponseModel(
        status=True,
        data= {
            'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'Bearer'
        },
        message="Operation Successful."
    )


@router.get('/me', response_model=ResponseModel)
def get_me(user: UserBaseSchema = Depends(get_current_user)):
    return ResponseModel(
        status=True,
        data=user,
        message="Operation Successful."
    )
