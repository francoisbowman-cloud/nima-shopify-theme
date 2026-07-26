# Nima Image Server

Servicio propio (FastAPI + Pillow + rembg) para tratar fotos de catálogo sin depender de
URLs públicas intermedias: recibe el archivo directo por HTTP y devuelve el resultado
directo en la respuesta. Pensado para reemplazar el rodeo de subir/bajar archivos vía
Shopify Files que estaba bloqueado (ver `shopify-staged-upload-signature-bug` en memoria
del proyecto).

## Endpoints

Todos (salvo `/health`) requieren `Authorization: Bearer <API_TOKEN>`.

| Endpoint | Método | Body (multipart/form-data) | Devuelve |
|---|---|---|---|
| `/health` | GET | — | `{"status": "ok"}` |
| `/crop` | POST | `file`, `box` (JSON `[left,top,right,bottom]`) | PNG |
| `/remove-bg` | POST | `file` | PNG (fondo transparente) |
| `/replace-bg` | POST | `file`, `color` (hex, ej `#FBF8F3`) | PNG |
| `/resize` | POST | `file`, `width?`, `height?`, `mode` (`fit`\|`stretch`) | PNG |
| `/palette` | POST | `file`, `colors` (int) | JSON con hex + conteo |
| `/process` | POST | `file`, `pipeline` (JSON, lista de pasos encadenados) | PNG |

`/process` es el endpoint principal: encadena crop → remove-bg → replace-bg → resize en
una sola llamada. Ejemplo de `pipeline`:

```json
[
  {"op": "crop", "box": [0, 0, 900, 1200]},
  {"op": "remove-bg"},
  {"op": "replace-bg", "color": "#FBF8F3"},
  {"op": "resize", "width": 1600, "mode": "fit"}
]
```

## Ejemplo de uso

```bash
curl -X POST https://<tu-servicio>.up.railway.app/process \
  -H "Authorization: Bearer $API_TOKEN" \
  -F "file=@crop_hammock_blue3.jpg" \
  -F 'pipeline=[{"op":"remove-bg"},{"op":"replace-bg","color":"#FBF8F3"},{"op":"resize","width":1600,"mode":"fit"}]' \
  -o resultado.png
```

## Deploy en Railway

1. `railway login` (o desde el dashboard, "New Project" → "Deploy from GitHub repo").
2. Apuntar el proyecto de Railway a esta carpeta (`image-server/`) si el repo tiene más
   de una app — en el dashboard: Settings → "Root Directory" = `image-server`.
3. Railway detecta el `Dockerfile` automáticamente y lo usa para el build.
4. Configurar la variable de entorno `API_TOKEN` (Settings → Variables) con un valor
   random largo (ej. `openssl rand -hex 32`) — sin esto el servicio devuelve 500 en
   cualquier endpoint protegido, a propósito, para no quedar abierto por defecto.
5. Railway asigna dominio público automáticamente (Settings → Networking → "Generate
   Domain") si se quiere acceder desde afuera del proyecto.

## Local

```bash
cd image-server
pip install -r requirements.txt
API_TOKEN=dev-token uvicorn app.main:app --reload
```

La primera llamada a `remove-bg`/`replace-bg`/`process` descarga el modelo de `rembg`
(~176MB, `u2net`) la primera vez que se usa — puede tardar unos segundos extra en el
primer request tanto local como en Railway.
