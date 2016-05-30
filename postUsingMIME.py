# Recipe from http://code.activestate.com/recipes/146306/

import mimetypes


def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name (str), value (str)) elements for regular form fields.
    files is a sequence of (name (str), filename (str), content (byte)) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib instance
    """
    BOUNDARY = b'----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = b'\r\n'
    L = []
    for (key, value) in fields.items():
        L.append(b'--' + BOUNDARY)
        L.append( ('Content-Disposition: form-data; name="%s"' % str(key)).encode() )
        L.append(b'')
        L.append(value.encode() )
    for (key, filename, value) in files:
        L.append(b'--' + BOUNDARY)
        L.append( ('Content-Disposition: form-data; name="%s"; filename="%s"' % (str(key), str(filename))).encode() )
        L.append( ('Content-Type: %s' % get_content_type(str(filename))).encode() )
        L.append(b'')
        L.append(value)
    L.append(b'--' + BOUNDARY + b'--')
    L.append(b'')
    body = CRLF.join(L)
    content_type = b'multipart/form-data; boundary=' + BOUNDARY
    return content_type, body


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
