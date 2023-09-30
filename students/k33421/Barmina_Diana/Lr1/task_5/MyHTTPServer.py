import socket
from email.parser import Parser
from Request import Request
from Response import Response


MAX_LINE = 64 * 1024
MAX_HEADERS = 100


class MyHTTPServer:
    def __init__(self, host, port):
        self.port = port
        self.host = host
        self.conn = None
        self.data = {}  # {subject: [grades]}

    def serve_forever(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_sock.bind((self.host, self.port))
            server_sock.listen(10)
            print("Server is running...")
            while True:
                client_socket, _ = server_sock.accept()
                try:
                    self.serve_client(client_socket)
                except Exception as e:
                    print('Client serving failed', e)
        finally:
            server_sock.close()

    def serve_client(self, conn):
        try:
            req = self.parse_request(conn)
            response = self.handle_request(req)
            self.send_response(conn, response)
        except ConnectionResetError:
            conn = None
        except Exception as e:
            print("Error", e)
        if conn:
            conn.close()

    def parse_request(self, conn):
        rfile = conn.makefile('rb')
        method, target, ver = self.parse_request_line(rfile)

        headers = self.parse_headers(rfile)

        host = headers.get('Host')
        if not host:
            raise Exception('Host header is missing')

        return Request(method, target, ver, headers, rfile)

    def parse_request_line(self, rfile):
        raw = rfile.readline(MAX_LINE + 1)
        if len(raw) > MAX_LINE:
            raise Exception('Request line is too long')

        req_line = str(raw, 'iso-8859-1').rstrip('\r\n')
        words = req_line.split()
        if len(words) != 3:
            raise Exception('Malformed request line')

        method, target, ver = words
        if ver != 'HTTP/1.1':
            raise Exception('Unexpected HTTP version')

        return method, target, ver


    @staticmethod
    def parse_headers(rfile):
        headers = []

        while True:
            line = rfile.readline(MAX_LINE + 1)
            if len(line) > MAX_LINE:
                raise Exception('Header line is too long')

            if line in (b'\r\n', b'\n', b''):
                break

            headers.append(line)
            if len(headers) > MAX_HEADERS:
                raise Exception('Too many headers')

        sheaders = b''.join(headers).decode('iso-8859-1')
        return Parser().parsestr(sheaders)

    def handle_request(self, req):
        content_type = 'text/html; charset=utf-8'
        body = str()
        if req.path == '/' and req.method == 'POST':
            subject = req.query_body['subject'][0]
            grade = req.query_body['grade'][0]
            try:
                self.data[subject].append(grade)
            except KeyError:
                self.data[subject] = [grade]
            body = self.handle_get()
        elif req.method == 'GET':
            if req.path == '/add_grade':
                with open("index.html", encoding='utf-8') as index:
                    body1 = index.read()
                body = body1
            elif req.path == '/':
                body = self.handle_get()
        body = body.encode('utf-8')
        headers = [('Content-Type', content_type),
                   ('Content-Length', len(body))]
        return Response(200, 'OK', headers, body)

    def handle_get(self):
        body = """
                <!DOCTYPE html>
                <html lang="ru">
                <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body>
                    <h2><center>Ведомость</center></h2>
                    <table style="border-collapse: collapse; width: 70%;" align="center">
                        <tr>
                            <th style="border: 1px solid black; padding: 4px;">Предмет</th>
                            <th style="border: 1px solid black; padding: 4px;">Оценка</th>
                        </tr>
                """
        for subject, grades in self.data.items():
            for grade in grades:
                body += f"""<tr>
                                <td style="border: 1px solid black; padding: 4px;">{subject}</td>
                                <td style="border: 1px solid black; padding: 4px;">{grade}</td>
                            </tr>
                        """

        body += """
                </table>
                    <form action="/add_grade" style="padding: 10px;">
                        <center><input type="submit" value="Добавить данные"></center>
                    </form>
            </body>
        </html>
                """
        return body

    @staticmethod
    def send_response(conn, resp):
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
        wfile.write(status_line.encode('iso-8859-1'))

        if resp.headers:
            for (key, value) in resp.headers:
                header_line = f'{key}: {value}\r\n'
                wfile.write(header_line.encode('iso-8859-1'))

        wfile.write(b'\r\n')

        if resp.body:
            wfile.write(resp.body)

        wfile.flush()
        wfile.close()
