from .. import objects, tags

class Test_FacultybyTags(object):
    def setup(self):
        tags.reset()

        self.f = objects.Faculty('foo', 'bar', '', '')
        self.g = objects.Faculty('zip', 'zap', '', '')

        tags.add_faculty(self.f, ['a', 'b'])
        tags.add_faculty(self.g, ['a', 'c'])

    def teardown(self):
        tags.reset

    def test_a(self):
        assert self.f in tags.get_faculty_by_tags(['a'])
        assert self.g in tags.get_faculty_by_tags(['a'])

    def test_b(self):
        assert self.f in tags.get_faculty_by_tags(['b'])
        assert self.g not in tags.get_faculty_by_tags(['b'])

    def test_c(self):
        assert self.f not in tags.get_faculty_by_tags(['c'])
        assert self.g in tags.get_faculty_by_tags(['c'])
        
    def test_d(self):
        assert self.f not in tags.get_faculty_by_tags(['d'])
        assert self.g not in tags.get_faculty_by_tags(['d'])

    def test_all(self):
        x = tags.get_all_faculty()
        assert self.f in x
        assert self.g in x
