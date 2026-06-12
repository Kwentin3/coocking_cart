FROM node:22.19.0-slim AS build

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY frontend/package*.json ./
RUN npm ci

COPY frontend ./

ARG NEXT_PUBLIC_MVP_ENTRY_URL=/mvp
ENV NEXT_PUBLIC_MVP_ENTRY_URL=${NEXT_PUBLIC_MVP_ENTRY_URL}
ARG NEXT_PUBLIC_LANDING_ASSET_DEBUG_IDS=false
ENV NEXT_PUBLIC_LANDING_ASSET_DEBUG_IDS=${NEXT_PUBLIC_LANDING_ASSET_DEBUG_IDS}

RUN npm run build
RUN npm prune --omit=dev

FROM node:22.19.0-slim AS runtime

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=build /app ./

EXPOSE 3000

CMD ["npm", "run", "start", "--", "--hostname", "0.0.0.0", "--port", "3000"]
