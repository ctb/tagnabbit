from sets import ImmutableSet

class Faculty(object):
    def __init__(self, first_name, last_name, blurb, url):
        self.first_name = first_name
        self.last_name = last_name
        self.blurb = blurb
        self.url = url

        self.hashset = ImmutableSet([ 'first=%s' % first_name,
                                      'last=%s' % last_name])

    def __hash__(self):
        return hash(self.hashset)
