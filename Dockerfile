FROM python:3.9.12-slim-bullseye

ARG GECKODRIVER_VER="v0.30.0"
ARG FIREFOX_VER="99.0"
ARG CRON_SPEC="24 3 * * 0"
#ARG CRON_SPEC="*/5 * * * *"

ENV PROJ_DIR="/WORK"
ENV LOG_FILE="${PROJ_DIR}/crawler.log"

ADD . ${PROJ_DIR}
WORKDIR ${PROJ_DIR}

# Install cron
RUN apt-get update && apt-get -y install --no-install-recommends cron

# Add latest FireFox
RUN set -x && \
    apt-get install -y libx11-xcb1 libdbus-glib-1-2 curl bzip2 packagekit-gtk3-module libasound2 && \
    curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 && \
    tar -jxf firefox-* && \
    mv firefox /opt/ && \
    chmod 755 /opt/firefox && \
    chmod 755 /opt/firefox/firefox && \
    ln -s /opt/firefox/firefox /usr/bin/firefox
  
# Add geckodriver
RUN set -x && \
    curl -sSLO https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz && \
    tar zxf geckodriver-*.tar.gz && \
    mv geckodriver /usr/bin/

# Clean useless files
RUN apt-get purge -y curl bzip2 && \
    rm -rf /tmp/* /usr/share/doc/* /var/cache/* /var/lib/apt/lists/* /var/tmp/* && \
    rm firefox-*.tar.bz2 && \
    rm geckodriver-*.tar.gz

# Python dependencies
RUN \
    pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

RUN echo "${CRON_SPEC} /usr/local/bin/python ${PROJ_DIR}/pyremax/runSpider.py >> ${LOG_FILE} 2>&1" > ${PROJ_DIR}/crontab
RUN touch ${LOG_FILE} # Needed for the tail
RUN crontab ${PROJ_DIR}/crontab
RUN crontab -l
CMD cron && tail -f ${LOG_FILE}
