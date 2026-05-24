# Server audit report: 91.132.48.224 v0.1

- Статус: read-only audit completed
- Дата: 2026-05-24
- Target server: `91.132.48.224`
- SSH user: `root`
- Target domain: `coocking-cart.speechbattle.com`

## Назначение

Документ фиксирует результат первого read-only аудита сервера для будущего деплоя Demo MVP.

Аудит не является деплоем. На сервере не менялись файлы, контейнеры, Docker networks, Traefik, firewall, DNS или TLS settings.

## Выполненные read-only проверки

Проверены:

- SSH доступ;
- текущий пользователь и рабочая директория;
- hostname и kernel;
- Docker version;
- Docker Compose version;
- запущенные containers;
- Docker networks;
- Docker volumes;
- Docker images;
- наличие `/opt`;
- наличие `/root`;
- наличие Traefik-related paths;
- network attachment для Traefik containers.

Не читались:

- `.env` файлы;
- SSH private keys;
- Traefik secrets;
- application secrets;
- credentials.

## Server basics

| Field | Observed value |
| --- | --- |
| SSH user | `root` |
| Working directory | `/root` |
| Hostname | `r1121293` |
| Kernel | `Linux 5.10.0-32-amd64` |
| Docker | `Docker version 28.5.2` |
| Docker Compose | `Docker Compose version v5.1.0` |

## Running containers

Read-only `docker ps` showed running containers:

| Container | Image | Status / notes |
| --- | --- | --- |
| `platform-edge-traefik` | `traefik:v3.5` | Public Traefik, ports `80` and `443` exposed |
| `platform-edge-smoke-traefik` | `traefik:v3.5` | Smoke Traefik, localhost ports `18080` and `18443` |
| `platform-edge-smoke-service` | `traefik/whoami:v1.11.0` | Smoke service |
| `doctorbridge-landing` | `nginx:1.27-alpine` | Existing service |
| `seminar-app` | `ghcr.io/kwentin3/seminar` | Existing service |
| `seminar-app-smoke` | `ghcr.io/kwentin3/seminar` | Existing smoke service |
| `switerkoff-app` | `switerkoff-app` | Existing service |
| `switerkoff-db` | `postgres:16-alpine` | Existing database container |

These containers must not be stopped, restarted, removed or reconfigured without a separate reviewed deployment task.

## Docker networks

Read-only `docker network ls` showed:

| Network | Driver | Scope |
| --- | --- | --- |
| `bridge` | bridge | local |
| `edge` | bridge | local |
| `host` | host | local |
| `none` | null | local |
| `switerkoff_internal` | bridge | local |

Traefik containers are attached to `edge`.

## Docker volumes and images

- `docker volume ls` returned no named volumes.
- `docker images` shows existing images for Traefik, nginx, seminar, switerkoff and postgres.
- There are multiple dangling images. No cleanup was performed.

## Filesystem observations

Read-only listing showed:

- `/opt/platform/traefik` exists.
- `/opt/doctorbridge` exists.
- `/opt/seminar` exists.
- `/opt/switerkoff` exists.
- `/opt/containerd` exists.
- `/root/.ssh` exists.
- `/root/backups`, `/root/switerkoff-runtime` and `/root/switerkoff-safe-backups` exist.

No files were opened or modified.

## Traefik observations

- Public Traefik container: `platform-edge-traefik`.
- Smoke Traefik container: `platform-edge-smoke-traefik`.
- Traefik image: `traefik:v3.5`.
- Traefik-related path found: `/opt/platform/traefik`.
- Public Traefik exposes `80` and `443`.
- Traefik containers are attached to Docker network `edge`.

TLS policy, certresolver name and Traefik email/resolver settings were not confirmed because configuration files and `.env` files were not read in this audit.

## Deployment implications

Future Demo MVP deployment should:

- avoid touching existing containers;
- use a reviewed Docker network strategy, likely involving `edge` if Traefik routing requires it;
- avoid changing Traefik until labels/config are reviewed;
- keep real `.env` outside Git;
- choose a deploy path that does not conflict with `/opt/platform`, `/opt/seminar`, `/opt/doctorbridge` or `/opt/switerkoff`;
- include a dry-run/review step before deployment.

## Still unknown

- Safe app deploy path.
- Final Docker network strategy.
- Traefik certresolver name.
- Current TLS policy.
- Whether a dedicated app network is needed in addition to `edge`.
- Where real `.env` should live on the server.
- Logs retention policy.
- Backup policy for SQLite/demo data.
- Owner of secrets and environment values.

## Forbidden until next task

- Deploying the application.
- Creating production Docker Compose config.
- Changing Traefik.
- Changing Docker networks.
- Stopping or restarting containers.
- Removing dangling images.
- Issuing TLS certificates.
- Changing firewall or DNS.
- Writing secrets to repository.
