import nowslides


# Custom parsers
def team_top4(e, v, p):
    return('<div>TEAM TOP4</div>')


def listing(e, v, p):
    html = '<ul class="list">'

    for li in e['contents']:
        html += '<li><span class="number">' + str(li['number']) + '</span>'
        html += '<span class="title">' + li['title'] + '</span>'
        html += '<span class="explanation">' + li['explanation'] + '</span></li>\n'

    html += "</ul>"

    return html


# Load the yaml
y = nowslides.load_yaml('./example.yaml')

# List of custom parsers
elparsers = [
    team_top4,
    listing
]

# List of custom variables
variables = {
    'teamName': "Name of Team",
    'teamN': 20,
    'teamResponsNo': 10,
    'teamResponsPercentage': '50%'
}

html = nowslides.render_presentation(y, variables, elparsers)

print(html)
