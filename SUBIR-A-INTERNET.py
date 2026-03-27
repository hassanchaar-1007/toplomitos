"""
TOP LOMITOS - Subir a Internet (v4)
Reutiliza el mismo sitio en Netlify para mantener el mismo link siempre.
"""
import http.client, json, ssl, os, sys, webbrowser, zipfile, io, time

script_dir = os.path.dirname(os.path.abspath(__file__))
html_file = os.path.join(script_dir, "top-lomitos-system.html")
token_file = os.path.join(script_dir, ".netlify-token")
site_id_file = os.path.join(script_dir, ".netlify-site-id")

print()
print("=" * 50)
print("  TOP LOMITOS - Subir a Internet (v4)")
print("=" * 50)
print()

if not os.path.exists(html_file):
    print("ERROR: No se encontro 'top-lomitos-system.html'")
    input("\nEnter para cerrar...")
    sys.exit(1)

# Token
token = ""
if os.path.exists(token_file):
    with open(token_file) as f:
        token = f.read().strip()
if token:
    print(f"[OK] Token: {token[:8]}...")
else:
    print("Necesitas un token de Netlify (gratis).")
    input("Enter para abrir navegador...")
    webbrowser.open("https://app.netlify.com/user/applications#personal-access-tokens")
    print()
    print('1. Crea cuenta (o usa Google)')
    print('2. "New access token" > nombre: TopLomitos')
    print('3. Copia el token')
    print()
    token = input("Pega token: ").strip()
    if not token:
        input("Sin token. Enter para cerrar...")
        sys.exit(1)
    with open(token_file, "w") as f:
        f.write(token)
    print("[OK] Token guardado.\n")

# Leer HTML
with open(html_file, "rb") as f:
    html_bytes = f.read()
print(f"[1] HTML leido: {len(html_bytes):,} bytes")

# Crear ZIP
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("index.html", html_bytes.decode("utf-8"))
    zf.writestr("_headers", "/*\n  Content-Type: text/html; charset=UTF-8\n")
    zf.writestr("netlify.toml", '[build]\n  publish = "."\n\n[[headers]]\n  for = "/*"\n  [headers.values]\n    Content-Type = "text/html; charset=UTF-8"\n')
zip_bytes = buf.getvalue()
print(f"[2] ZIP creado: {len(zip_bytes):,} bytes")

ctx = ssl.create_default_context()

def api(method, path, body=None, ctype="application/json"):
    c = http.client.HTTPSConnection("api.netlify.com", timeout=60, context=ctx)
    h = {"Authorization": f"Bearer {token}"}
    if ctype: h["Content-Type"] = ctype
    if body: h["Content-Length"] = str(len(body) if isinstance(body, bytes) else len(body.encode()))
    c.request(method, path, body=body, headers=h)
    r = c.getresponse()
    raw = r.read().decode()
    c.close()
    try: return r.status, json.loads(raw)
    except: return r.status, {"_raw": raw[:500]}

# Buscar o crear sitio
site_id = ""
site_url = ""

# Intentar leer site_id guardado
if os.path.exists(site_id_file):
    with open(site_id_file) as f:
        site_id = f.read().strip()
    # Verificar que el sitio sigue existiendo
    print(f"[3] Verificando sitio existente ({site_id[:12]}...)...")
    st, d = api("GET", f"/api/v1/sites/{site_id}")
    if st == 200:
        site_url = d.get("ssl_url", d.get("url", "???"))
        print(f"    [OK] Sitio encontrado: {site_url}")
    else:
        print(f"    Sitio no encontrado (HTTP {st}), creando nuevo...")
        site_id = ""

if not site_id:
    print("[3] Creando sitio en Netlify...")
    st, d = api("POST", "/api/v1/sites", body="{}")
    print(f"    HTTP {st}")
    if st not in (200, 201) or "id" not in d:
        print(f"    ERROR: {json.dumps(d, indent=2)[:400]}")
        if st == 401:
            print("    Token invalido. Borra .netlify-token y ejecuta de nuevo.")
            try: os.remove(token_file)
            except: pass
        input("\nEnter para cerrar...")
        sys.exit(1)
    site_id = d["id"]
    site_url = d.get("ssl_url", d.get("url", "???"))
    site_name = d.get("name", "???")
    print(f"    Sitio: {site_name}")
    print(f"    URL: {site_url}")
    # Guardar site_id para reutilizar
    with open(site_id_file, "w") as f:
        f.write(site_id)
    print(f"    [OK] Site ID guardado para futuras actualizaciones")

# Deploy ZIP
print("[4] Subiendo ZIP...")
st2, d2 = api("POST", f"/api/v1/sites/{site_id}/deploys", body=zip_bytes, ctype="application/zip")
print(f"    HTTP {st2}")
if st2 not in (200, 201):
    print(f"    ERROR: {json.dumps(d2, indent=2)[:400]}")
    input("\nEnter para cerrar...")
    sys.exit(1)

deploy_id = d2.get("id", "")
deploy_state = d2.get("state", "???")
deploy_url = d2.get("ssl_url", site_url)
print(f"    Deploy ID: {deploy_id}")
print(f"    Estado: {deploy_state}")
print(f"    URL: {deploy_url}")

# Esperar
print("[5] Esperando que este listo...")
final_url = deploy_url
for i in range(40):
    time.sleep(3)
    st3, d3 = api("GET", f"/api/v1/deploys/{deploy_id}")
    state = d3.get("state", "???")
    final_url = d3.get("ssl_url", deploy_url)
    print(f"    ...{state} ({i+1}/40)")
    if state == "ready":
        print(f"    [OK] Deploy listo!")
        break
    if state in ("error", "failed"):
        print(f"    ERROR en deploy: {d3.get('error_message', '???')}")
        input("\nEnter para cerrar...")
        sys.exit(1)

print()
print("=" * 50)
print()
print("  LISTO! Sistema actualizado:")
print()
print(f"  {final_url}")
print()
print("=" * 50)
print()
print("PINes: Admin=0000 Mozo=1111 Cajera=6666 Cocina=8888")
print()

# Guardar link
with open(os.path.join(script_dir, "MI-LINK.txt"), "w") as f:
    f.write(f"Link: {final_url}\nAdmin: 0000\nMozo: 1111\nCajera: 6666\nCocina: 8888\n")
print("Link guardado en MI-LINK.txt")

# Abrir
try:
    webbrowser.open(final_url)
    print(f"Abriendo {final_url}")
except:
    pass

print()
input("Enter para cerrar...")
