from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse


def get_custom_swagger_ui_html(
        *,
        openapi_url: str,
        title: str = "Swagger UI",
) -> HTMLResponse:

    html = get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "defaultModelExpandDepth": 1,
        },
    )

    html_content = html.body.decode()

    custom_css = """
    <style>
        /* Убираем ВСЕ серые фоны в Schemas */
        .swagger-ui .models .model-container,
        .swagger-ui .models .model-container:hover,
        .swagger-ui .model-box,
        .swagger-ui .model-box:hover,
        .swagger-ui .models h4,
        .swagger-ui .models h5,
        .swagger-ui section.models .model-container,
        .swagger-ui .model .model-box {
            background: #ffffff !important;
            box-shadow: none !important;
            border: 1px solid #e0e0e0 !important;
        }

        /* Убираем серый фон у заголовков */
        .swagger-ui .models h4,
        .swagger-ui .models h5,
        .swagger-ui .model-title {
            background: transparent !important;
        }

        /* Убираем рамки и фоны у вложенных элементов */
        .swagger-ui .model .property,
        .swagger-ui .model .property-required,
        .swagger-ui .model .property-optional {
            background: transparent !important;
        }

        /* Делаем все блоки белыми */
        .swagger-ui .scheme-container,
        .swagger-ui .models-control,
        .swagger-ui .model {
            background: #ffffff !important;
        }

        /* Hover эффекты делаем минимальными */
        .swagger-ui .model-container:hover,
        .swagger-ui .model-box:hover {
            background: #fafafa !important;
        }

        /* Убираем тени */
        .swagger-ui .model-container {
            box-shadow: none !important;
        }
    </style>
    """

    html_content = html_content.replace("</body>", f"{custom_css}</body>")

    return HTMLResponse(content=html_content, status_code=200)