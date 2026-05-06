import json
from typing import Annotated

from fastapi.encoders import jsonable_encoder
from openai import OpenAI
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

from ..models import Todos
from ..database import SessionLocal
from ..Roaters.auth import get_current_user

router = APIRouter(prefix="/AI", tags=["AI"])


OPENAI_API_KEY = "sk-YgtPjS1D2bcRzo1T0vludER7Gql4x54TL8iVjVp6EHGi4Yll"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/")
async def root(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail="user is not available")
    todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
    if todos is None:
        raise HTTPException(status_code=401, detail="todos is not available")

    # with OpenAI(base_url='https://api.gapgpt.app/v1', api_key=OPENAI_API_KEY) as client:
    #     selected_id = choose_todo_for_user(db, user.get("id"), client)
    #     print("Suggested todo id:", selected_id)

    todo_str: str = json.dumps(jsonable_encoder(todos), ensure_ascii=False)
    with OpenAI(base_url='https://api.gapgpt.app/v1', api_key=OPENAI_API_KEY) as client:
        message_to_ai: str = f"""You are a task prioritization assistant.
    From the provided list of todos, select ONE task that the user should work on next.
    Base your decision on the data provided in the list and your power of decision-making 
    and do not take very serious 'priority' of tasks in list.
    Return your response STRICTLY in this JSON format:
    {{
      "selected_id": <integer>,
      "reason": <str>
    }}
    
    Rules:
    - Only output a valid JSON object.
    - reason must be one line maximum.
    - Do not include markdown.
    - Do not include any extra fields.
    
    Todo List (JSON array):
    {todo_str}"""
        print(message_to_ai)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": message_to_ai}
            ]
        )
        ai_content = response.choices[0].message.content
        try:
            result = json.loads(ai_content)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=str(e))
        return result