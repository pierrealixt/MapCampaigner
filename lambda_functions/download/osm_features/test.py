import unittest
import warnings
from lambda_function import lambda_handler


class TestCase(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings(
            "ignore", 
            category=ResourceWarning, 
            message="unclosed.*<ssl.SSLSocket.*>")     

    def test_run(self):
        event = {
            'campaign_uuid': 'cabbf57b1ac3410cafdd6d64abb1c893' 
        }
        lambda_handler(event, {})

if __name__ == '__main__':
    unittest.main()