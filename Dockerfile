# Builds the site with Pelican and serves it with nginx under a sub-path (default /labs/srg/home/).
# The host's own nginx reverse-proxies to this container; see "Deploying to the ICS server" in README.md.

# ---- build ----------------------------------------------------------------
FROM python:3.12-slim AS build
ARG SRG_BASE_PATH=/labs/srg/home
ENV SRG_BASE_PATH=${SRG_BASE_PATH}
WORKDIR /src
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pelican content -s publishconf_ics.py -o /site

# ---- serve ----------------------------------------------------------------
FROM nginx:1.27-alpine
ARG SRG_BASE_PATH=/labs/srg/home
COPY docker/nginx.conf.template /tmp/default.conf.template
RUN sed "s#__BASE__#${SRG_BASE_PATH}#g" /tmp/default.conf.template > /etc/nginx/conf.d/default.conf \
 && rm /tmp/default.conf.template
COPY --from=build /site /usr/share/nginx/html${SRG_BASE_PATH}
EXPOSE 80
