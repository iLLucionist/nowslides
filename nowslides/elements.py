def notfound(e, v, p):
    return simple('ELEMENT NOT FOUND')


def simple(text, v={}, tag='p'):
    return f'<{tag}>{text}</{tag}>'.format(**v)


def p(e, v, p):
    return simple(e, v)


def h1(e, v, p):
    return simple(e, v, 'h1')


def h2(e, v, p):
    return simple(e, v, 'h2')


def h3(e, v, p):
    return simple(e, v, 'h3')


def h4(e, v, p):
    return simple(e, v, 'h4')


def h5(e, v, p):
    return simple(e, v, 'h5')


def ul(e, v, p):
    html = '<ul>'

    for li in e:
        html += '<li>' + li + '</li>\n'

    html += '</ul>'

    return html


def div(e, v, p):
    from .main import render_elements

    cls = e.get('class', None)

    html = '<div class="' + cls + '">'
    html += ''.join(render_elements(e['contents'], v, p))
    html += "</div>"

    return html
