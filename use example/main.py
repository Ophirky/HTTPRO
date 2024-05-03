from httpro.app import App
from httpro import functions
import httpro
import json

app = App()

@app.route(b"/")
def home_page(request) -> bytes:
    """
    Home page of the website.
    :param request: The request of the file.
    :return bytes: THe html page.
    """
    return httpro.read_file("use example/index.html")


@app.route(b"/contact")
def contact_page(request) -> bytes:
    """
        Allows the user send a question
        :param request: The request given by the client.
        :return bytes: The uri of the request.
    """
    return httpro.read_file("use example/contact.html")


@app.route(b"/question", return_body_type=".txt")
def get_question(request):
    """
        Gets the question that the user sent
        :param request: The request given by the client.
        :return bytes: The uri of the request.
    """
    ans = functions.dict_to_bytes(json.loads(request.BODY))
    return b"username: " + ans[b"mail"] + b", question: " + ans[b"question"]


# Set the 404 page #
app.set_four_o_four("use example/404.html")

# Start the local http server #
app.run(port=80)
