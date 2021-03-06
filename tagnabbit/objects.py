# -*- coding: iso-8859-1 -*-

from sets import ImmutableSet

class Faculty(object):
    def __init__(self, first_name, last_name, blurb, url):
        self.id = None
        self.first_name = first_name
        self.last_name = last_name
        self.blurb = blurb
        self.url = url

        self.hashset = ImmutableSet([ 'first=%s' % first_name,
                                      'last=%s' % last_name])

    def __hash__(self):
        return hash(self.hashset)

class Project(object):
    def __init__(self, title, blurb, url):
        self.id = None
        self.title = title
        self.blurb = blurb
        self.url = url
        self.faculty = ""

        self.hashset = self.title

    def __hash__(self):
        return hash(self.hashset)
