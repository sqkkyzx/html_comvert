import time
import os
from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import logging
import json

from playwright.async_api import async_playwright
import toml


access_address = os.environ.get("ACCESS_ADDRESS").replace("/", "")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title='网页转换服务',
    description='仅供 API 调用的 HTML/URL 转换服务。',
    version="1.0",
    docs_url="/"
)
app.mount("/tmp", StaticFiles(directory="tmp"), name="static")


class Html(BaseModel):
    text: str = Field(None, description="Html 字符串，使用 html 相关接口时必填")
    width: int = Field(1920, description="生成的图片宽度，转换为图片时必填")
    height: int = Field(1080, description="生成的图片高度，转换为图片时必填")
    filename: str = Field(None, description="希望保存的文件名，选填。默认为当前时间戳。")


class Url(BaseModel):
    url: str = Field(None, description="URL 链接，必填")
    width: int = Field(1920, description="生成的图片宽度，仅转换图片时生效")
    height: int = Field(1080, description="生成的图片高度，仅转换图片时生效")
    javascript: str = Field("", description="打开网页后执行的 JS 脚本，用于修改页面元素等，仅 url 相关接口生效")
    filename: str = Field(None, description="希望保存的文件名，选填。默认为当前时间戳。")


class Result(BaseModel):
    url: str = Field(None, description="生成文件的下载链接")
    filename: str = Field(None, description="生成文件的文件名")


class Json(BaseModel):
    data: dict = Field(None, description="必填，json 内容")
    filename: str = Field(None, description="必填，文件名前缀")


@app.post("/html2pdf", tags=["HTML"], summary='HTML 字符串转 PDF 文档', response_model=Result)
async def html2pdf(html: Html):
    logging.info("RUNING HTML_TO_PDF...")
    Result.filename = html.filename if html.filename else str(time.time_ns())

    file_path = f"tmp/pdf/{Result.filename}.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()

        await page.set_content(html.text)
        await page.wait_for_load_state('networkidle')

        await page.pdf(path=file_path)
        await browser.close()

    Result.url = f"http://{access_address}/tmp/pdf/{Result.filename}.pdf"
    logging.info(Result.url)

    return Result


@app.post("/html2png", tags=["HTML"], summary='HTML 字符串转 PNG 图片', response_model=Result)
async def html2img(html: Html):
    logging.info("RUNING HTML_TO_PNG...")

    Result.filename = html.filename if html.filename else str(time.time_ns())

    file_path = f"tmp/png/{Result.filename}.png"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()

        await page.set_viewport_size({"width": html.width, "height": html.height})

        await page.set_content(html.text)
        await page.wait_for_load_state('networkidle')

        await page.screenshot(path=file_path, full_page=True)
        await browser.close()

    Result.url = f"http://{access_address}/tmp/png/{Result.filename}.png"
    logging.info(Result.url)

    return Result


@app.post("/url2pdf", tags=["URL"], summary='URL 字符串转 PDF 文档', response_model=Result)
async def html2pdf(url: Url):
    logging.info("RUNING HTML_TO_PDF...")
    Result.filename = url.filename if url.filename else str(time.time_ns())

    file_path = f"tmp/pdf/{Result.filename}.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()

        await page.goto(url.url)
        await page.wait_for_load_state('networkidle')

        await page.pdf(path=file_path)
        await browser.close()

    Result.url = f"http://{access_address}/tmp/pdf/{Result.filename}.pdf"
    logging.info(Result.url)

    return Result


@app.post("/url2png", tags=["URL"], summary='URL 网页转 PNG 图片', response_model=Result)
async def url2img(url: Url):
    logging.info(f"Convert {url.url} to png...")
    Result.filename = url.filename if url.filename else str(time.time_ns())

    file_path = f"tmp/png/{Result.filename}.png"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()

        await page.set_viewport_size({"width": url.width, "height": url.height})

        await page.goto(url.url)
        await page.wait_for_load_state('networkidle')

        await page.evaluate(url.javascript.replace("\\n", ""))
        await page.wait_for_load_state('networkidle')

        await page.screenshot(path=file_path, full_page=True, type="png")
        await browser.close()

    Result.url = f"http://{access_address}/tmp/png/{Result.filename}.png"
    logging.info(Result.url)

    return Result


@app.post("/json2html", tags=["HTML"], summary='字典对象网页显示 JSON', response_model=Result)
async def json2html(data: Json):
    logging.info(f"Convert {data.data} to html...")

    Result.filename = F"{data.filename.replace(' ', '_')}-{time.time_ns()}"

    # 构建完整的文件路径
    file_path = f"tmp/json/{Result.filename}.html"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    json_str = json.dumps(data.data, indent=4, ensure_ascii=False)

    toml_str = toml.dumps(data.data)

    html_str = f"""
    <!DOCTYPE html>
    <html>
    <head><title>{Result.filename}</title></head>
    <body>
        <h2>{data.filename}</h2>
        <h2>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}<h2>
        <h3>TOML</h3><pre>{toml_str}</pre>    
        <h3>JSON</h3><pre>{json_str}</pre>
    </body>
    </html>
    """

    with open(file_path, 'w') as file:
        file.write(html_str)

    print(f"文件已保存到: {file_path}")

    Result.url = f"http://{access_address}/tmp/json/{Result.filename}.html"
    logging.info(Result.url)
    return Result
