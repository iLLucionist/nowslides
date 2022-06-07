import os

from mako.template import Template

from . import elements as _elparsers
from .utils import Cache, load_yaml, module_to_dict
from copy import deepcopy


_TPLDIR = os.path.join(os.path.dirname(__file__), 'templates')
_TPLCACHE = Cache(lambda f: Template(
    filename=os.path.join(get_template_path(), f + '.html')), disable=True)
_ELPARSERS = module_to_dict(_elparsers)
_DEBUG = False


def get_template_path():
    return _TPLDIR


def set_template_path(path):
    global _TPLDIR
    _TPLDIR = path


def get_template(name): return _TPLCACHE[name]


def _log(msg):
    if _DEBUG is True:
        print(msg)


def get_intent(intent, y):
    if intent not in y:
        raise ValueError(f'Intent {intent} not found in spec')
    return y[intent]


def parse_intent(intent, variables):
    v = variables | {'tplpath': _TPLDIR}

    intent['master'] = intent['master'].format(**v)
    for x in ('js', 'css'):
        if x in intent:
            intent[x] = list(map(lambda y: y.format(**v), intent[x]))

    return intent


def render_presentation(y, variables={}, elparsers=[], tplpath=_TPLDIR):
    """
    Render a YAML-based presentation.

    Arguments:
    y -- the YAML-syntax that contains the presentation format
    variables -- variables that should be available in the presentation
    elparsers -- the custom element parsers (simple functions)
    """
    _log('Rendering presentation...')
    # Get presentation YAML
    y = y.get('presentation', y)
    y = deepcopy(y)

    # Combine variables in yaml-template with those provided to this function
    variables = y.get('variables', {}) | variables
    # Only retain entries in elparses that are callable
    elparsers = {p.__name__: p for p in filter(callable, elparsers)}
    # Combine internal elparsers with those provided to this function
    elparsers = _ELPARSERS | elparsers

    # Log names of vars and elparsers that are provided
    tmp_v = ' '.join(variables.keys())
    tmp_p = ' '.join(elparsers.keys())
    _log(f'  {len(variables)} variables: {tmp_v}')
    _log(f'  {len(elparsers)} element parsers: {tmp_p}')

    # Render all the slides iteratively
    slides = "\n".join(render_slides(y['slides'], variables, elparsers))

    # Parse the intent
    intent = parse_intent(get_intent(y['intent'], y), variables)

    # Combine all values that may be referenced in the yaml-template
    # and then render that to html using the master tempalte
    values = variables | intent | {'slides': slides}
    html = get_template(intent['master']).render(**values)

    # Log which templates are loaded and used
    tmp_t = ' '.join(_TPLCACHE.keys())
    _log(f'  {len(_TPLCACHE)} templates autoloaded and used: {tmp_t}')

    return html


def render_slides(slides, variables, elparsers):
    """
    Render all slides to html.

    Arguments:
    slides -- the yaml-syntax slides
    variables -- variables that may be references on the slides
    elparsers -- the elparsers that may be referenced on the slides
    """
    # i is required to provide every slide a unique html div id
    for slide, i in zip(slides, range(1, len(slides) + 1)):
        yield render_slide(slide, i, variables, elparsers)


def render_slide(slide, i, variables, elparsers):
    """
    Render a slide to html.

    Arguments:
    slide -- the yaml-syntax slide
    i -- the number of the slide (for unique html div id)
    variables -- variables that may be references on the slides
    elparsers -- the elparsers that may be referenced on the slides
    """

    # The unique div id for html
    no = f'slide-{i}'
    # Extract slide type
    typ = slide['type'].replace(' ', '-')
    # Get variant of slide type (will be html class name)
    variant = slide.get('variant', '')
    # Get extra variables that may be provided in the slide yaml-syntax
    extravars = slide.get('variables', {})
    # Make class name for slide div
    cls = variant + ' ' + typ

    # Remove variables from yaml slide dict. The reason is that this function
    # will think they are custom elements, but they do not exist
    for k in ('type', 'variant', 'variables'):
        slide.pop(k, None)

    # Render all the slide areas and the elements listed
    content = render_areas(slide, variables, elparsers)

    # Render the slide using specified template
    variables['areas'] = content
    variables['variant'] = variant
    variables['pageno'] = i
    content = get_template(typ).render(**variables | extravars)

    return f'<div id="{no}" class="{cls} slide">\n{content}\n</div>'


def render_areas(areas, variables, elparsers):
    """
    Render all areas in slides.

    Arguments:
    areas -- the yaml-syntax for all areas in slide
    variables -- variables that may be provided
    elparsers -- dict of all element parsers
    """

    content = {}
    for area, elements in areas.items():
        content[area] = ''.join(render_elements(elements, variables,
                                                elparsers))
    return content


def render_elements(elements, variables, elparsers):
    for element in elements:
        yield str(render_element(element, variables,
                                 elparsers))


def render_element(element, variables, elparsers):
    """
    Renders an element using elparsers. IF elparsers not found, will
    render the 'notfound' element from _ELPARSERS.

    Arguments:
    element -- the yaml-syntax for the element
    variables -- variables that may be provided
    elparsers -- the provided element parsers
    """
    etype, element = next(iter(element.items()))
    eparser = elparsers.get(etype, elparsers['notfound'])
    return(str(eparser(element, variables, elparsers)))
