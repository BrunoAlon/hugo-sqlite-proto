#!/usr/bin/env python3
import unittest
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from migrar import transformar, normalizar_fecha, etiquetas_json, FECHA_NULA

class TestMigrar(unittest.TestCase):
    def test_transformar_basico(self):
        entrada = {
            "slug": "hola-hugo",
            "title": "Hola Hugo",
            "date": "2026-10-15",
            "draft": False,
            "tags": ["hugo", "static"],
            "body": "Contenido en **Markdown**.",
        }
        post, attrs = transformar(entrada, user_id=1)
        self.assertEqual(post["clean"], "hola-hugo")
        self.assertEqual(post["status"], "public")
        self.assertEqual(post["created_at"], "2026-10-15 00:00:00")
        self.assertEqual(post["updated_at"], FECHA_NULA)
        dict_attrs = dict(attrs)
        self.assertEqual(dict_attrs["title"], "Hola Hugo")
        self.assertEqual(dict_attrs["body"], "Contenido en **Markdown**.")
        self.assertEqual(dict_attrs["tags"], '["hugo", "static"]')

    def test_transformar_borrador_sin_tags(self):
        entrada = {
            "slug": "borrador",
            "title": "En borrador",
            "date": "2026-11-01",
            "draft": True,
            "tags": [],
            "body": "Texto",
        }
        post, attrs = transformar(entrada)
        self.assertEqual(post["status"], "draft")
        self.assertEqual(dict(attrs)["tags"], "[]")

if __name__ == "__main__":
    unittest.main()
