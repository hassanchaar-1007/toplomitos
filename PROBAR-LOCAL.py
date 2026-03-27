"""
TOP LOMITOS - Servidor Local para Pruebas
Abre http://localhost:8000 en el navegador
"""
import http.server, webbrowser, os, shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Copy HTML to index.html for easy access
if os.path.exists("top-lomitos-system.html"):
    shutil.copy2("top-lomitos-system.html", "index.html")
    print("Copiado top-lomitos-system.html -> index.html")

port = 8000
url = f"http://localhost:{port}"

print()
print("=" * 50)
print(f"  Servidor local en: {url}")
print("  Ctrl+C para detener")
print("=" * 50)
print()

webbrowser.open(url)

handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(("", port), handler)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServidor detenido.")
