from unittest import TestCase
from test_utils.assertions import DiffTestCaseMixin

class TestAssertions(TestCase, DiffTestCaseMixin):
    """
    Tests to test assertions in test utils.
    """

    def test_assert_no_diff_dict(self):
        dict1 = {'I love': 'you'}
        dict2 = {'I love': 'moo'}
        try:
            self.failIfDiff(dict1, dict2)
        except AssertionError, e:
            self.failIfDiff(e.message, """\n--- First \n\n+++ Second \n\n@@ -1,1 +1,1 @@\n\n-'I love':'you'\n+'I love':'moo'\n""")

    def test_assert_no_diff_list(self):
        list1 = ['I love', 'you']
        list2 = ['I love', 'to moo']
        try:
            self.failIfDiff(list1, list2)
        except AssertionError, e:
            self.failIfDiff(e.message, """\n--- First \n\n+++ Second \n\n@@ -1,2 +1,2 @@\n\n 'I love'\n-'you'\n+'to moo'\n""")
