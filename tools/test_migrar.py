#!/usr/bin/env python3
import unittest
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from migrar import transformar, transformar_pagina, normalizar_fecha, etiquetas_json, FECHA_NULA

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
        self.assertEqual(dict(attrs)["title"], "Hola Hugo")

    def test_transformar_pagina(self):
        pagina = {
            "slug": "about",
            "title": "Sobre BrunoAlon",
            "date": "2026-10-01",
            "draft": False,
            "body": "Página sobre mí",
        }
        fila = transformar_pagina(pagina, user_id=1)
        self.assertEqual(fila["clean"], "about")
        self.assertEqual(fila["title"], "Sobre BrunoAlon")
        self.assertEqual(fila["public"], 1)
        self.assertEqual(fila["created_at"], "2026-10-01 00:00:00")

if __name__ == "__main__":
    unittest.main()
