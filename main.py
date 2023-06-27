# python-multipart is required for file upload
from fastapi import FastAPI, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

import fitz  # python -m pip install --upgrade pymupdf
import re

app = FastAPI(title="Ean-128 Etiketten")
api_app = FastAPI(title="Ean-128 Etiketten API")
app.mount('/api', api_app)

origins = ["http://localhost/*", "http://localhost:8000/*", "http://markmolenmaker.github.io", "https://markmolenmaker.github.io" ]
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

app.mount("/", StaticFiles(directory="static", html=True), name="static")


def list_join(seq):
    """ Join a sequence of lists into a single list, much like str.join
        will join a sequence of strings into a single string.
    """
    return [x for sub in seq for x in sub]


code128B_mapping = dict((chr(c), [98, c+64] if c < 32 else [c-32]) for c in range(128))
code128C_mapping = dict([(u'%02d' % i, [i]) for i in range(100)] + [(u'%d' % i, [100, 16+i]) for i in range(10)])
code128_chars = u''.join(chr(c) for c in [212] + list(range(33,126+1)) + list(range(200,211+1)))


def encode128(s):
    """ Code 128 conversion for a font as described at
        https://en.wikipedia.org/wiki/Code_128 and downloaded
        from http://www.barcodelink.net/barcode-font.php
        Only encodes ASCII characters, does not take advantage of
        FNC4 for bytes with the upper bit set. Control characters
        are not optimized and expand to 2 characters each.
        Coded for https://stackoverflow.com/q/52710760/5987
    """
    if s.isdigit() and len(s) >= 2:
        # use Code 128C, pairs of digits
        codes = [105] + list_join(code128C_mapping[s[i:i+2]] for i in range(0, len(s), 2))
    else:
        # use Code 128B and shift for Code 128A
        codes = [104] + list_join(code128B_mapping[c] for c in s)
    check_digit = (codes[0] + sum(i * x for i,x in enumerate(codes))) % 103
    codes.append(check_digit)
    codes.append(106) # stop code
    return u''.join(code128_chars[x] for x in codes)


def convert_barcodes_pdf(file_path):
    doc = fitz.open(file_path)

    fontfile = "code128.ttf"
    pattern = re.compile(r"^(\d{6,8})\n(\d+)")

    product_info = []  # [(artikel_code, ean_code), ...]

    for page in doc:
        page.insert_font(fontname="code128",  fontfile=fontfile)
        page.wrap_contents()

        textpage = page.get_textpage()
        for block in textpage.extractBLOCKS():
            text = block[4]

            match = pattern.match(text)
            if match:
                product_info.append((match.group(1), match.group(2)))

        images = page.get_images(full=True)
        for index in range(len(images)):
            image = images[index]
            xref = image[0]
            bbox = page.get_image_bbox(image)

            page.delete_image(xref)

            # page.draw_rect(bbox, color=(0, 0, 0), width=1)
            page.insert_textbox(bbox, encode128(product_info[index][1]), fontsize=16, fontname='code128',
                                color=(0, 0, 0), align=fitz.TEXT_ALIGN_RIGHT)

            bbox = fitz.Rect(bbox[0], bbox[1] - 4, bbox[2] - 4, bbox[3])
            page.insert_textbox(bbox, 'MM / EAN-128', fontsize=4, fontname='Helvetica',
                                color=(0, 0, 0), align=fitz.TEXT_ALIGN_RIGHT)

        doc.save("output.pdf", garbage=4, deflate=True, clean=True)

    doc.close()


@api_app.get("/v1/debug")
async def say_hello():
    return {'message': 'Hello World!'}


@api_app.post("/v1/file/upload")
async def file_upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open("tmpf.pdf", "wb") as f:
            f.write(contents)
        convert_barcodes_pdf("tmpf.pdf")

    except Exception as e:
        print(e)
        return {'message': 'Something went wrong'}

    finally:
        file.file.close()

    return FileResponse("output.pdf")
