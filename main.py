import os
import tempfile
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile
from markitdown import MarkItDown

load_dotenv()

API_KEY = os.getenv("API_KEY", None)

MAX_SIZE = 10 * 1024 * 1024  # 10MB

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
    file: UploadFile, api_key: Annotated[str | None, Depends(get_api_key)] = None
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Forbidden")

    content = await file.read(MAX_SIZE + 1)
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # NOTE: Reset file position so it is read from the start
    await file.seek(0)

    try:
        with tempfile.NamedTemporaryFile(
            suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

            result = md.convert(temp_file_path)

            print("Result is")
            print(result)

        return {"markdown": result.markdown}

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
