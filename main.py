from fastapi import FastAPI, UploadFile
from markitdown import MarkItDown

app = FastAPI()

md = MarkItDown(enable_plugins=True)


@app.post("/convert")
async def convert_markdown(file: UploadFile):
    result = md.convert(file.file)

    return {"markdown": result.markdown}
