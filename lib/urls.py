""" URLs """
import webbrowser as _webbrowser
__all__ = ['get_urls', 'open']
wiki = 'https://github.com/cbott/830_scouting_forms/wiki/Team-830%27s-2014-match-scouting-form'
bugreport = 'https://github.com/cbott/830_scouting_forms/wiki/Reporting-a-bug'
newissue = 'https://github.com/cbott/830_scouting_forms/issues/new'

_urls = dir()

def get_urls():
    urls = {}
    for url in _urls:
        if url.startswith('_'):
            continue
        urls[url] = globals()[url]
    return urls

def open(url):
    url = get_urls()[url] or url
    _webbrowser.open(url)
