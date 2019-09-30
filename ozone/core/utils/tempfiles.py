from contextlib import contextmanager
import tempfile
from pathlib import Path
import mimetypes

from django.http import FileResponse


@contextmanager
def capture_temp_file(name):
    """ Write data to a temporary file and load it as BytesIO

    with capture_temp_file('myfile.txt') as (path, output):
        with path.open('wb') as f:
            f.write(b'hello world')

    output.name == 'myfile.txt'
    output.read() == b'hello world'
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        output = tempfile.TemporaryFile()
        output.name = name

        yield path, output

        with path.open('rb') as f:
            output.write(f.read())
            output.seek(0)


def django_file_response(file):
    resp = FileResponse(file)
    resp['Content-Type'] = mimetypes.guess_type(file.name)
    resp['Content-Disposition'] = f'attachment; filename={file.name}'
    return resp
