from fastapi import FastAPI, Depends, HTTPException, status
from PIL import Image
import PIL.ImageOps
from fastapi import File,  Response, UploadFile
from io import BytesIO
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()


@app.get("/prime/{number}")
async def is_prime(n):
    if n.isnumeric():
        number = int(n)
        if number < 9223372036854775807:
            if number < 2:
                return {"To nie liczba pierwsza"}
            else:
                if number == 2:
                    return {"To liczba pierwsza"}
                else:
                    for i in range(2, number):
                        if number % i == 0:
                            return {"To nie liczba pierwsza"}
                    return {"To liczba pierwsza"}
        else:
            return {"Niepoprawna liczba"}
    else:
        return {"Nalezy podac liczbe calkowita"}


@app.post("/picture/invert/")
async def picture_invert(file: UploadFile = File(...)):
    picture = PIL.ImageOps.invert(Image.open(file.filename))
    picture = image_to_bytes(picture)
    return Response(content=picture, media_type="image/jpeg")


def image_to_bytes(picture):
    img_byte_arr = BytesIO()
    picture.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()


fake_user = {
    "pip3": {
        "username": "pip3",
        "hashed_password": "fakehashedpip3",
    },
}


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    user = get_user(fake_user, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowe dane logowania",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Uzytkownik nieaktywny")
    return current_user


@app.post("/time")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_user.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=400, detail="Nieprawidłowe dane logowania")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(
            status_code=400, detail="Nieprawidłowe dane logowania")
    now = datetime.now()
    return "Godzina: " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
