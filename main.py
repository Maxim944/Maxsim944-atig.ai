from fastapi import FastAPI
from pydantic import BaseModel
from playwright.sync_api import sync_playwright

app = FastAPI()

class Request(BaseModel):
    query: str


def search(query):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.google.com")

        page.fill("textarea[name='q']", query)
        page.keyboard.press("Enter")

        page.wait_for_selector("h3")
        results = page.query_selector_all("h3")

        output = []
        for r in results[:3]:
            output.append(r.inner_text())

        browser.close()
        return "\n".join(output)


@app.post("/agent")
def agent(req: Request):
    result = search(req.query)
    return {"answer": result}