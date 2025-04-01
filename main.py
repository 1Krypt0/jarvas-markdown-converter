import os
import tempfile
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile
from markitdown import MarkItDown

load_dotenv()

API_KEY = os.getenv("API_KEY", None)

MAX_SIZE = 50 * 1024 * 1024  # 50MB

MAX_UPLOADS = 5

if not API_KEY:
    raise Exception("Api key not found. Shutting Down")

app = FastAPI()

md = MarkItDown(enable_plugins=True)


def get_api_key(authorization: Annotated[str | None, Header()]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Invalid or missing Authorization header"
        )

    api_key = authorization.split(" ", 1)[1]
    return api_key


@app.post("/convert")
async def convert_markdown(
    files: list[UploadFile], api_key: Annotated[str | None, Depends(get_api_key)] = None
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Forbidden")

    if len(files) > MAX_UPLOADS:
        raise HTTPException(
            status_code=413, detail=f"Cannot upload more than {MAX_UPLOADS} at a time"
        )

    for file in files:
        # NOTE: Not using file.size as it might not be present on the request
        size = len(await file.read(MAX_SIZE + 1))

        if size > MAX_SIZE:
            raise HTTPException(status_code=413, detail="File too large")

    results = []

    for file in files:
        await file.seek(0)  # NOTE: Reset file position so it is read from the start

        try:
            with tempfile.NamedTemporaryFile(
                suffix=os.path.splitext(file.filename)[1]
            ) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name

                res = md.convert(temp_file_path)

            results.append(res.markdown)

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"files": results}
