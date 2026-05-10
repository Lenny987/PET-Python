from app.docs import get_custom_swagger_ui_html

def test_get_custom_swagger_ui_html():
    result = get_custom_swagger_ui_html(openapi_url="/openapi.json")
    assert result.status_code == 200
    assert b"</body>" in result.body