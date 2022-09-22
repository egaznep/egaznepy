# a python server that serves local files within a directory.
# based on python3-server but displays .wav content with HTML5 audio tags

import html
import io
import os
import socketserver
import sys
import urllib
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler

import typer


class WavHandler(SimpleHTTPRequestHandler):
    """A handler for .wav files. Instead of just printing their names, we now
    serve them using HTML5 audio objects.
    """

    def list_directory(self, path):
        """Overridden to have <audio> elements for .wav files."""
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(self.path, errors="surrogatepass")
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = "Directory listing for %s" % displaypath
        r.append(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
            '"http://www.w3.org/TR/html4/strict.dtd">'
        )
        r.append("<html>\n<head>")
        r.append(
            '<meta http-equiv="Content-Type" ' 'content="text/html; charset=%s">' % enc
        )
        r.append("<title>%s</title>\n</head>" % title)
        r.append("<body>\n<h1>%s</h1>" % title)
        r.append('\n<p><a href="../">Upper directory</a></p>')
        r.append("<hr>\n<ul>")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /

            r.append(
                '<li><a href="%s">%s</a></li>'
                % (
                    urllib.parse.quote(linkname, errors="surrogatepass"),
                    html.escape(displayname, quote=False),
                )
            )
            if ".wav" in linkname:
                r.append(
                    '<audio controls preload="none"><source src="%s"></audio>' % (name)
                )

        r.append("</ul>\n<hr>\n</body>\n</html>\n")
        encoded = "\n".join(r).encode(enc, "surrogateescape")
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f


WavHandler.extensions_map[".wav"] = "audio/wav"
WavHandler.extensions_map[""] = "text/plain"


def main(port: int = 8080):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), WavHandler) as httpd:
        print(f"Listening on port {port}. Press Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    typer.run(main)
