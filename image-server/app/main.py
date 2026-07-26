import io
import json
import os
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from PIL import Image
from rembg import remove

app = FastAPI(title="Nima Image Server")
security = HTTPBearer(auto_error=False)

API_TOKEN = os.environ.get("API_TOKEN")


def check_auth(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> None:
    if not API_TOKEN:
        raise HTTPException(500, "API_TOKEN not configured on the server")
    if creds is None or creds.credentials != API_TOKEN:
        raise HTTPException(401, "Invalid or missing bearer token")


def load_image(data: bytes) -> Image.Image:
    try:
        return Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception as exc:
        raise HTTPException(400, f"Could not read image: {exc}")


def encode_png(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def png_response(img: Image.Image) -> Response:
    return Response(content=encode_png(img), media_type="image/png")


def apply_crop(img: Image.Image, box: list[int]) -> Image.Image:
    if len(box) != 4:
        raise HTTPException(400, "crop box must be [left, top, right, bottom]")
    left, top, right, bottom = box
    if left >= right or top >= bottom:
        raise HTTPException(400, "invalid crop box")
    return img.crop((left, top, right, bottom))


def apply_remove_bg(img: Image.Image) -> Image.Image:
    return remove(img)


def apply_replace_bg(img: Image.Image, color: str) -> Image.Image:
    fg = remove(img)
    bg = Image.new("RGBA", fg.size, color)
    bg.alpha_composite(fg)
    return bg


def apply_resize(img: Image.Image, width: Optional[int], height: Optional[int], mode: str) -> Image.Image:
    if not width and not height:
        raise HTTPException(400, "resize requires width and/or height")
    w0, h0 = img.size
    if mode == "fit":
        if width and height:
            img.thumbnail((width, height), Image.LANCZOS)
            return img
        if width:
            height = round(h0 * width / w0)
        else:
            width = round(w0 * height / h0)
        return img.resize((width, height), Image.LANCZOS)
    if mode == "stretch":
        width = width or w0
        height = height or h0
        return img.resize((width, height), Image.LANCZOS)
    raise HTTPException(400, "mode must be 'fit' or 'stretch'")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/remove-bg", dependencies=[Depends(check_auth)])
async def remove_bg(file: UploadFile = File(...)):
    img = load_image(await file.read())
    return png_response(apply_remove_bg(img))


@app.post("/replace-bg", dependencies=[Depends(check_auth)])
async def replace_bg(file: UploadFile = File(...), color: str = Form("#FFFFFF")):
    img = load_image(await file.read())
    return png_response(apply_replace_bg(img, color))


@app.post("/crop", dependencies=[Depends(check_auth)])
async def crop(file: UploadFile = File(...), box: str = Form(...)):
    img = load_image(await file.read())
    parsed = json.loads(box)
    return png_response(apply_crop(img, parsed))


@app.post("/resize", dependencies=[Depends(check_auth)])
async def resize(
    file: UploadFile = File(...),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    mode: str = Form("fit"),
):
    img = load_image(await file.read())
    return png_response(apply_resize(img, width, height, mode))


@app.post("/palette", dependencies=[Depends(check_auth)])
async def palette(file: UploadFile = File(...), colors: int = Form(6)):
    img = load_image(await file.read()).convert("RGB")
    quantized = img.quantize(colors=colors, method=Image.MEDIANCUT)
    raw_palette = quantized.getpalette()[: colors * 3]
    counts = sorted(quantized.getcolors(), reverse=True)
    result = []
    for count, index in counts[:colors]:
        r, g, b = raw_palette[index * 3 : index * 3 + 3]
        result.append({"hex": f"#{r:02x}{g:02x}{b:02x}", "count": count})
    return {"colors": result}


@app.post("/process", dependencies=[Depends(check_auth)])
async def process(file: UploadFile = File(...), pipeline: str = Form(...)):
    """
    pipeline: JSON list of steps, applied in order, e.g.
    [{"op": "crop", "box": [0,0,900,1200]},
     {"op": "remove-bg"},
     {"op": "replace-bg", "color": "#FBF8F3"},
     {"op": "resize", "width": 1600, "mode": "fit"}]
    """
    img = load_image(await file.read())
    steps = json.loads(pipeline)
    for step in steps:
        op = step.get("op")
        if op == "crop":
            img = apply_crop(img, step["box"])
        elif op == "remove-bg":
            img = apply_remove_bg(img)
        elif op == "replace-bg":
            img = apply_replace_bg(img, step.get("color", "#FFFFFF"))
        elif op == "resize":
            img = apply_resize(img, step.get("width"), step.get("height"), step.get("mode", "fit"))
        else:
            raise HTTPException(400, f"unknown op: {op}")
    return png_response(img)
