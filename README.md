
<img src="Logo.png">
# HTTPRO
http library for website development.  
This library helps python web developers make a website easily without the need to  
learn about how everything works in the backend side of things.  
  
# How to use?  
## _**Create the app and start the server**_
The first step to creating a website you need to init the app (a.k.a the server).
Write the following lines to create the app.
`from httpro.app import App
app = App()
`
<br>

## _**Start the server**_
To start the server you will need to run the following command. in your main file.
`app.run()`
The app will run on port `80` and the host will set to `127.0.0.1` by default.

You can change th eport to run the program on using the next command.
`app.run(port=8080)`

You can change the host ip using the `host` argument.
`app.run(host="198.35.67.1")`
<br>

## _**Create a route**_
Once you created your app you will need to create a page that your users can view.
to do that you will need to use the `route` decorator.
Under the decorator there will be a function that will return the response body (if there is one).
```
@app.route(b"/")
def home_page(request: httpro.http_message.HttpMsg) -> bytes:
	return b"Hello"
```
This will create a page in the base route (`http://website.com`).
This page will be shown as a html page that contains the text "Hello".
<br>
## _**Generate an html page**_
To add a real html document to your route you can just read return to the route the file contents.
```
@app.route("/my_html")
def new_page(request:  httpro.http_parser.HttpParser) -> bytes:
	file_path = r"index.html"
	with open(file_path, "rb") as f:
		return f.read()
```
While this is a way to do it but there is an easier way. and more secure way to this.
```
@app.route("/my_html")
def new_page(request:  httpro.http_parser.HttpParser) -> bytes:
	file_path = r"index.html"
	return httpro.read_file(file_path)
```
This way is more secure and will guarantee that you won't try to open a file that does not exist and crash the program.
<br>

## _**Return No Html**_
To return something else then html you need to add the return_body_type argument to the route decorator.
```
@app.route(b"/jpg", return_body_type=".jpg")  
def new_page(request: httpro.http_parser.HttpParser) -> bytes:  
	file_path = r"use example/image.jpg"  
	return httpro.read_file(file_path)
```

Available file types:
File Type|Http Code
-|-
.html         | "text/html;charset=utf-8"
.jpg" |image/jpeg
.css" |text/css
.js" | ext/javascript; charset=UTF-8
.txt" |text/plain
.ico" |image/x-icon
.gif" |image/jpeg
.png" |image/png
<br>

# HttpParser
The HttpParser class allows you to use in a comfortable manner the client request.
## _**Properties**_
| Property     | Description                                                                                                                               |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| METHOD       | This is the method of the request (GET, POST, DELETE, PUT)                                                                                |
| URI          | The uri of the request (/home, /404)                                                                                                      |
| HTTP_VERSION | The version of the http (http/1.1)                                                                                                        |
| QUERY_PARAMS | The query parameters given in the function in the form of a dictionary - Example: /hello?id=45&name="Ron" -> {"id": "45", "name":"Ron"}   |
| HEADERS      | The headers in the request (Content-Length, Content-Type), stored in a dictionary - {"Content-Length": "45", "Content-Type":"text/plain"} |
| BODY         | The body of the request.                                                                                                                  |

<br>

# HttpMsg
This will allow you to create a custom http message.
