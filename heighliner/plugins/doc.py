def register(*args, **kwargs):
    return ['doc']


def validate(*args, **kwargs):
    return kwargs['config']


def do(*args, **kwargs):
    print 'Running heighliner doc action'
