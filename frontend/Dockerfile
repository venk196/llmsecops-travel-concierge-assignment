FROM nginxinc/nginx-unprivileged:1.31.6-alpine3.24
USER root
RUN apk upgrade --no-cache
USER 101
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 8080

