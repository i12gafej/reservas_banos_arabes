# Frontend Staff (Vite + React)

Este directorio contiene la aplicación **staff** (panel interno) construida con Vite + React + TypeScript.

---
## Requisitos previos

1. **Node.js 18 LTS o 20 LTS** (se recomienda la misma versión usada en los Dockerfiles: `node:20-alpine`).
2. Gestor de paquetes **npm** ≥ 9 (o `pnpm`/`yarn`, ajusta los comandos si los prefieres).
3. (Opcional) Docker + Docker Compose si vas a levantar el entorno dentro de contenedores.

---
## Instalación inicial

```bash
# dentro de aplicacion/frontend/staff
npm install
```

Esto descargará las dependencias listadas en `package.json` (React 18, Vite 5, etc.).

---
## Actualizar a las versiones más recientes (recomendado)

El comando `npm outdated` muestra las diferencias entre tu versión instalada, la *Wanted* (según semver) y la *Latest* en el registro npm. Para saltar a las últimas releases estables ejecuta lo siguiente:

```bash
# 1. Actualiza librerías de UI y enrutado (sin breaking mayor)
npm install @mui/material@latest @mui/icons-material@latest react-router-dom@latest vite@latest

# 2. Ecosistema ESLint / TypeScript
npm install -D eslint@latest \
               @typescript-eslint/parser@latest \
               @typescript-eslint/eslint-plugin@latest \
               eslint-plugin-react-hooks@latest

# 3. (Opcional) Migrar a React 19 beta
# Solo si quieres probarlo; React 18 sigue siendo estable.
# npm install react@latest react-dom@latest @types/react@latest @types/react-dom@latest

# 4. Reparar vulnerabilidades menores y sub-dependencias obsoletas
npm audit fix --force
```

> **Nota**: si algún paquete continúa anclado a versiones obsoletas (por ejemplo `glob@7` o `rimraf@3`), puedes forzar una versión superior mediante el campo `overrides` en tu `package.json`.

---
## Scripts útiles

```bash
npm run dev        # arranca Vite con HMR (http://localhost:5173)
npm run build      # genera build de producción en dist/
npm run preview    # previsualiza el build localmente
npm run lint       # ejecuta ESLint con TypeScript
```

---
## Uso con Docker

El proyecto incluye dos Dockerfiles:

1. **Dockerfile.dev** – para desarrollo con hot-reload. Se monta el código como volumen y se expone `5173`.
2. **Dockerfile** – para crear una imagen de producción basada en Nginx que sirve los archivos estáticos de `dist/`.

Ejemplo de servicio dentro de `docker-compose.yml` (modo desarrollo):

```yaml
frontend:
  build:
    context: ./frontend/staff
    dockerfile: Dockerfile.dev
  volumes:
    - ./frontend/staff:/app
    - /app/node_modules      # evita montar node_modules del host
  ports:
    - "5173:5173"
  environment:
    - CHOKIDAR_USEPOLLING=1  # máxima fiabilidad de HMR en Windows
```

Con esto, cualquier cambio en `src/` se reflejará al instante en el navegador.

---
## ￼Buenas prácticas de mantenimiento

- Ejecuta `npm outdated` cada cierto tiempo para detectar nuevas majors.
- Mantén tu CI (GitHub Actions, GitLab CI, etc.) con Dependabot o Renovate para recibir PRs automáticos de actualización.
- Revisa el *changelog* de React, Vite y MUI antes de saltar de versión mayor para detectar cambios de API.
- Si usas **pnpm workspaces** o **Turborepo**, recuerda añadir esta app a la lista de workspaces.

¡Listo! Tu proyecto **staff** quedará preparado con dependencias actualizadas y un procedimiento claro para mantenerlas al día. 



---

## Interfaz
Botones: https://www.npmjs.com/package/reactive-button
Formularios: https://react-hook-form.com/