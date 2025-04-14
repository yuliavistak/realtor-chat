from fastapi import FastAPI
from renter import main


app = FastAPI()


# class QueryRequest(BaseModel):
#     context_path: str
#     question: str
#     user_answer: str
#     classification: str


@app.post("/find_flat")
async def find_flat():
    main()
    return