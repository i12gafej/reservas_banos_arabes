────────────────────────────────────────
A. Backend Django (core)
────────────────────────────────────────
1. `DEBUG = False` en producción.  
2. `ALLOWED_HOSTS` restringido a los dominios reales.  
3. `SECRET_KEY` en variable de entorno (no en git).  
4. HTTPS obligatorio (`SECURE_SSL_REDIRECT = True`, HSTS, etc.).  
5. Cookies seguras:  
   • `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`  
   • `SESSION_COOKIE_HTTPONLY`, `CSRF_COOKIE_HTTPONLY`  
6. Protección CSRF: habilitada y verificada en todas las vistas que usan sesión.  
7. Cabeceras de seguridad (`SecurityMiddleware` ya añade varias):  
   • `X-Content-Type-Options: nosniff`  
   • `X-Frame-Options: DENY` o `SAMEORIGIN`  
   • `Referrer-Policy`, `Permissions-Policy`  
8. Rotación y longitud de contraseñas (validadores + `django-argon2` para hash fuerte).  
9. Límites de intentos de login (`django-axes`, `django-defender` o similar).  
10. Permisos granulares (`is_staff`, `is_superuser`, grupos, `@permission_required`).  
11. Control de CORS con `django-cors-headers` (orígenes explícitos).  

────────────────────────────────────────
B. API y autenticación externa
────────────────────────────────────────
12. Emisión de tokens (JWT con DRF SimpleJWT o similar) con expiración corta.  
13. Refresh tokens almacenados sólo en HttpOnly cookies.  
14. Scope/claims en el token (rol, permisos) y verificación servidor-side.  
15. Rate limiting en las vistas API (`django-ratelimit`, Nginx o API Gateway).  
16. Versionado de la API (`/api/v1/…`).  
17. Validación estricta de payloads (serializers → `validate_*`).  
18. Escape/filtrado del ORM (usar consultas parametrizadas; evitar `.extra()` sin cuidado).  

────────────────────────────────────────
C. Frontend React
────────────────────────────────────────
19. Almacenar sólo lo imprescindible en localStorage (evitar tokens largos).  
20. Protección XSS: escapar todo lo que venga de la API; usar `dangerouslySetInnerHTML` sólo con sanitizado.  
21. CSP en cabeceras para bloquear scripts externos.  
22. Rutas protegidas por guard (verificar JWT + permisos).  
23. Actualizaciones dependencias (npm audit).  

────────────────────────────────────────
D. Infraestructura / Nginx / Docker
────────────────────────────────────────
24. Nginx con TLS 1.2+ y certificados Let’s Encrypt (auto-renovación).  
25. Proxy pass sólo a contenedores internos (red Docker privada).  
26. Límites de subida (`client_max_body_size`) y tiempo de espera.  
27. Logs de acceso y error con retención y rotación.  
28. Imágenes Docker basadas en versiones oficiales minimalistas (slim, alpine).  
29. Variables de entorno inyectadas vía secrets (Docker Secrets, Vault, GitHub Actions secrets…).  
30. User non-root dentro de los contenedores.  
31. Actualización automática de parches (watchtower, CI build regular).  

────────────────────────────────────────
E. Base de datos
────────────────────────────────────────
32. Usuario Postgres con permisos mínimos (sin `SUPERUSER`).  
33. Contraseña fuerte en variable de entorno; opcionalmente certificado TLS entre Django y DB.  
34. Backups cifrados y probados (restore tests).  
35. Política de rotación de logs y `pg_audit` si necesitas auditoría fina.  

────────────────────────────────────────
F. DevOps / CI-CD
────────────────────────────────────────
36. Lint y tests de seguridad en CI (`bandit`, `safety`, `npm audit`).  
37. Scan de imágenes Docker (Trivy, Snyk).  
38. Branch protection + revisión de PR.  
39. Automatizar despliegues (IaC) para evitar cambios manuales.  

────────────────────────────────────────
G. Monitoreo y alertas
────────────────────────────────────────
40. Logs centralizados (ELK, Loki + Grafana).  
41. Alertas ante 5xx, picos de CPU, uso de disco, intentos de login fallidos.  
42. Tracing / APM (Sentry, Datadog) para detectar excepciones en backend y frontend.  

────────────────────────────────────────
Cómo avanzar
────────────────────────────────────────
• Empieza por la capa A (backend básico) y B (API/JWT), que te dan la base.  
• Después refuerza CORS, HTTPS y contenedores (capas C y D).  
• Finalmente añade monitoreo y CI-security.  
