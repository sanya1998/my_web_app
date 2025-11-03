from app.api.data.hotels.handlers import get_hotels
from app.common.constants.paths import PAGES_HOTELS_PATH, PAGES_PATH, PAGES_SSE_PATH
from app.common.helpers.api_version import VersionedAPIRouter
from app.config.common import settings
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

router = VersionedAPIRouter(prefix=PAGES_PATH)

templates = Jinja2Templates(directory="app/api/frontend/pages/templates")


@router.get(PAGES_HOTELS_PATH)
async def get_hotels_page(
    request: Request,
    hotels=Depends(get_hotels),
):  # todo: `): -> templates.TemplateResponse` ломает ручку
    return templates.TemplateResponse(
        name="hotels.html",
        context={"request": request, "hotels": hotels.content},
    )


# sse client
@router.get(PAGES_SSE_PATH, response_class=HTMLResponse)
async def get_sse_page():
    # flake8: noqa
    # TODO: templates
    # TODO: url to envs or env+const
    SSE_BASE_URL = f"http://{settings.API_HOST}:{settings.API_PORT}/"
    SSE_DATETIME_URL = "api/v1/sse/datetime"
    SSE_MESSAGES_URL = "api/v1/sse/messages"
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SSE Example</title>
        </head>            
        <body>
            <h1>Server-Sent Events with FastAPI</h1>
            <div id="datetime"></div>
            <div id="messages"></div>
            <script>  
                const baseUrl = '{SSE_BASE_URL}';
                const datetimeUrl = '{SSE_DATETIME_URL}';
                const messagesUrl = '{SSE_MESSAGES_URL}';
                
                const datetimeEventSource = new EventSource(baseUrl + datetimeUrl);  
                datetimeEventSource.onmessage = function(event) {{  
                    const datetimeDiv = document.getElementById("datetime");  
                    datetimeDiv.innerHTML = `<p>${{event.data}}</p>`;  
                }};
                
                const messagesEventSource = new EventSource(baseUrl + messagesUrl);  
                messagesEventSource.onmessage = function(event) {{  
                    const messagesDiv = document.getElementById("messages");  
                    messagesDiv.innerHTML += `<p>${{event.data}}</p>`;  
                }};  
            </script>  
        </body>
    </html> 
    """
    return HTMLResponse(content=html_content, status_code=200)
