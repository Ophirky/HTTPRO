"""
    AUTHOR: Ophir Nevo Michrowski
    DATE: 15/04/24
    DESCRIPTION: This is the app class. It will handle the webapp and the path.
"""
import glob
# Imports #
import socket
import select
import httpro.constants as consts
import logging
import re
import httpro.http_parser
import os

# global vars #
global readable_socks_list, writeable_socks_list, exception_socks_list

class App:
    """The Base for the web app."""

    # ---------- Constructor ---------- #
    def __init__(self):
        """This is the Constructor of the App class."""
        self.routes = dict()
        self.four_o_four = consts.FOUR_O_FOUR

    # ---------- Decorators ---------- #
    def route(self, route: bytes, return_body_type: str = ".html"):
        """
        Route decorator - adds the route to the routes' dictionary.
        :param route: the route for the uri
        :param return_body_type: The http msg type.
        :return: what the original function needs to return
        """

        def add_to_route_dict(original_function):
            """
            This is the decorator function
            :param original_function: original function that decorator decorates
            :return: what the original function needs to return
            """
            self.routes[route] = original_function.__call__, return_body_type

            def wrapper_function(*args, **kwargs):
                """
                This is the wrapper function.
                """
                raise Exception("This is a route function. It cannot be run.")

            return wrapper_function

        return add_to_route_dict

    # ---------- Private functions ---------- #
    @staticmethod
    def __receive_message(client_socket: socket) -> bool or httpro.http_parser.HttpParser:
        """
        Receives a message from a client
        :param client_socket:
        :return bool or HttpParser: False if the message is invalid, HttpParser with the message
        """
        try:
            message = client_socket.recv(consts.RECV_LENGTH)

            while b"\r\n\r\n" not in message:
                msg = client_socket.recv(consts.RECV_LENGTH)
                if not msg:
                    break
                message += msg

            try:
                content_length = int(re.search(rb'Content-Length: (\d+)', message).group(1))

                # Check if body was already received #
                if len(message.split(b'\r\n\r\n')) > 1 and len(message.split(b'\r\n\r\n')[1]) != content_length:
                    body = b''
                    # Receiving body #
                    while len(body) < content_length:
                        chunk = client_socket.recv(consts.RECV_LENGTH)
                        if not chunk:
                            break
                        body += chunk

                    message += body

            except AttributeError:
                logging.info(consts.NO_CONTENT_HEADER)

            except Exception as e:
                logging.exception(e)

            return httpro.http_parser.HttpParser(message)

        except Exception as e:
            logging.exception(e)

    def __handle_client(self, request: httpro.http_parser.HttpParser, client_socket: socket) -> None:
        """
        Handles the client input.
        :param request: The request that the server got.
        :param client_socket: The client socket.
        :return: None
        """
        response: httpro.http_message

        if request.URI is not None:
            if request.URI in self.routes.keys():
                response = httpro.http_message.HttpMsg(body=self.routes[request.URI][0](request),
                                                       content_type=self.routes[request.URI][1])

            elif not os.path.isfile(request.URI[1:].replace(b"%20", b" ")):
                with open(self.four_o_four, 'rb') as file:
                    response = httpro.http_message.HttpMsg(error_code=404, content_type=consts.MIME_TYPES[".html"],
                                                           body=file.read())
            # If uri does not have a special path #
            else:
                # extract requested file type from URL (html, jpg etc)
                file_type = os.path.splitext(request.URI)[1]

                # generate proper HTTP header
                file_data: bytes
                with open(request.URI[1:].replace(b"%20", b" "), 'rb') as f:
                    file_data = f.read()
                response = httpro.http_message.HttpMsg(content_type=consts.MIME_TYPES[file_type.decode()],
                                                       body=file_data)

            client_socket.send(response.build_message_bytes())

    # ---------- Public functions ---------- #
    def set_four_o_four(self, route: str) -> None:
        """
        Sets the route to the 404 page.
        :param route: The route to the 404 page html.
        :return: None
        """
        self.four_o_four = route

    def run(self, port=consts.PORT, host=consts.IP) -> None:
        """
        Starts the http server.
        :return: None
        """
        global readable_socks_list, writeable_socks_list, exception_socks_list

        # Setting up the socket #
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((host, port))
        sock.listen()

        socket_list = [sock]

        try:
            while True:
                readable_socks_list, writeable_socks_list, exception_socks_list = select.select(socket_list,
                                                                                                socket_list,
                                                                                                socket_list)

                for notified_socket in readable_socks_list:
                    if notified_socket == sock:  # checking for new connection #
                        client_socket, client_addr = sock.accept()
                        try:
                            logging.info(consts.NEW_CLIENT.format(client_addr[0], client_addr[1]))

                            message: httpro.http_parser.HttpParser = self.__receive_message(client_socket)
                            self.__handle_client(message, client_socket)

                        except Exception as e:
                            logging.exception(e)

                        finally:
                            client_socket.close()
        finally:
            sock.close()
