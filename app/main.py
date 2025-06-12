from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import employee, auth


app = FastAPI()
app.include_router(employee.app)
app.include_router(auth.app)

#fix me please : use specefic origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)












