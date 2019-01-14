from django.test import TestCase


def printer(msg):
    print("\n" + "-"*(len(msg) + 10))
    print("Got here #" + msg)
    print("-"*(len(msg) + 10) + "\n")

# printer("0")

class PlaceholderTest(TestCase):
    # printer("1")
    
    def setUp(self):
        # printer("2")    
        self.val = 1

    def failure_test(self):
        self.assertEqual(self.val, 3)
    
    def runTest(self):
        self.failure_test()