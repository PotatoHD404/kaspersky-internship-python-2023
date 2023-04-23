import json
import os
import re
import sys
import zipfile

import uvicorn
import uuid
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy import text

from database import SessionLocal
from dto import SearchFilters
from models import Search
from utils import apply_filters

app = FastAPI()

db = SessionLocal()

search_dir = "./search_directory"  # Задайте директорию для поиска файлов


def file_search(search_id: uuid.UUID, search_path: str, filters: SearchFilters) -> None:
    result = []

    for root_path, _, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root_path, file)
            is_zip = zipfile.is_zipfile(file_path)

            if is_zip:
                with zipfile.ZipFile(file_path, "r") as zip_file:
                    for zip_info in zip_file.infolist():
                        if zip_info.filename.endswith("/"):
                            continue

                        content = zip_file.read(zip_info.filename)

                        if apply_filters(file_path + "/" + zip_info.filename, content, filters, zip_info):
                            result.append(f"{file}/{zip_info.filename}")
            else:
                with open(file_path, "rb") as f:
                    content = f.read()

                if apply_filters(file_path, content, filters, None):
                    result.append(file_path)

    # searches[search_id] = {"finished": True, "paths": result}
    search = db.get(Search, search_id)
    search.finished = True
    result = list(map(lambda x: re.sub(r"\\", "/", x), result))
    search.paths = json.dumps(result)

    # commit the changes
    db.commit()


@app.on_event("startup")
def on_startup():
    db.execute(text("""
CREATE TABLE IF NOT EXISTS searches (
    id CHAR(36) PRIMARY KEY,
    finished BOOLEAN,
    paths TEXT
);
    """))


@app.post("/search")
async def root(filters: SearchFilters, background_tasks: BackgroundTasks):
    # req = {
    #     "text": "abc",
    #     "file_mask": "*a*.???",
    #     "size": {
    #         "value": 42000,
    #         "operator": "gt"
    #     },
    #     "creation_time": {
    #         "value": "2020-03-03T14:00:54Z",
    #         "operator": "eq"
    #     }
    # }

    search_id = uuid.uuid4()
    db.add(Search(id=search_id, finished=False, paths=str([])))

    # commit the changes
    db.commit()

    background_tasks.add_task(file_search, search_id, search_dir, filters)
    return {"search_id": search_id}


@app.get("/searches/{search_id}")
async def say_hello(search_id: str):
    uuid_regex = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    # if search_id not in searches:
    #     return JSONResponse(
    #         status_code=404,
    #         content={"message": f"Search was not found"},
    #     )
    # return searches[search_id]
    if not uuid_regex.match(search_id):
        # bad request
        return JSONResponse(
            status_code=400,
            content={"message": f"Search id is not valid"},
        )
    search = db.get(Search, uuid.UUID(search_id))
    if search is None:
        return JSONResponse(
            status_code=404,
            content={"message": f"Search was not found"},
        )
    if search.finished:
        return {"finished": True, "paths": json.loads(search.paths)}
    return {"finished": False}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        search_dir = sys.argv[1]
    uvicorn.run(app, host="0.0.0.0", port=8000)

