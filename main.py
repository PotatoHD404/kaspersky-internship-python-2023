import os
import zipfile

import uvicorn
import uuid
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from dto import SearchFilters
from utils import apply_filters

app = FastAPI()

search_dir = "search_directory"  # Задайте директорию для поиска файлов

searches = {}


def file_search(search_id, search_path, filters):
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

                        if apply_filters(zip_info.filename, content, filters):
                            result.append(f"{file}/{zip_info.filename}")
            else:
                with open(file_path, "rb") as f:
                    content = f.read()

                if apply_filters(file_path, content, filters):
                    result.append(file_path)

    searches[search_id] = {"finished": True, "paths": result}


@app.post("/search")
async def root(filters: SearchFilters):
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
    searches[search_id] = {"finished": False}
    file_search(search_id, search_dir, filters)
    return {"search_id": search_id}


@app.get("/searches/{search_id}")
async def say_hello(search_id: str):
    if search_id not in searches:
        return JSONResponse(
            status_code=404,
            content={"message": f"Search was not found"},
        )
    return searches[search_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
