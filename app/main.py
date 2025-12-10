from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .controllers import (
    period_controller,
    unit_school_associate_controller,
    user_workspace_controller,
    auth_controller,
    user_workspace_associate_controller,
    user_unal_controller,
    unit_unal_controller,
    user_unit_associate_controller,
    school_controller,
    headquarters_controller,
    school_headquarters_associate_controller,
    type_user_controller,
    type_user_association_controller,
    email_sender_controller,
    email_sender_unit_controller,
    email_sender_school_controller,
    email_sender_headquarters_controller,
    upload_controller,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    print("Hello World Endpoint Called")
    return {"Hello": "World"}


app.include_router(auth_controller.router)
app.include_router(upload_controller.router)
app.include_router(period_controller.router)
app.include_router(user_workspace_controller.router)
app.include_router(user_workspace_associate_controller.router)
app.include_router(user_unal_controller.router)
app.include_router(unit_unal_controller.router)
app.include_router(user_unit_associate_controller.router)
app.include_router(school_controller.router)
app.include_router(unit_school_associate_controller.router)
app.include_router(headquarters_controller.router)
app.include_router(school_headquarters_associate_controller.router)
app.include_router(type_user_controller.router)
app.include_router(type_user_association_controller.router)
app.include_router(email_sender_controller.router)
app.include_router(email_sender_unit_controller.router)
app.include_router(email_sender_school_controller.router)
app.include_router(email_sender_headquarters_controller.router)
