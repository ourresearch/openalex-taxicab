import unittest

from openalex_taxicab.harvest import has_pdf_magic


class HarvestPdfValidationTests(unittest.TestCase):
    def test_pdf_magic_allows_leading_whitespace(self):
        self.assertTrue(has_pdf_magic(b"\n\n%PDF-1.4\nbody\n%%EOF"))

    def test_pdf_magic_rejects_html_and_zip(self):
        self.assertFalse(has_pdf_magic(b"<h1>404 Not Found</h1>"))
        self.assertFalse(has_pdf_magic(b"PK\x03\x04not a pdf"))


if __name__ == "__main__":
    unittest.main()
