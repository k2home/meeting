FROM debian:trixie-slim

ARG VCS_REF=unknown
ARG VCS_BRANCH=unknown
ARG VCS_COMMIT_DATE=unknown

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MEETING_BUILD_COMMIT=\${VCS_REF} \
    MEETING_BUILD_COMMIT_DATE=\${VCS_COMMIT_DATE} \
    MEETING_BUILD_BRANCH=\${VCS_BRANCH}

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        libcairo2 \
        postgresql-client \
        python3.13 \
        python3.13-venv \
    && find /usr/lib/python3.13/ensurepip -type f -name 'setuptools-*.whl' -delete \
    && python3.13 -m venv /opt/venv \
    && find /usr/share/python-wheels -type f -name 'setuptools-*.whl' -delete \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt requirements-constraints.txt ./
RUN python -m pip install --upgrade pip 'setuptools>=78.1.1' \
    && pip install -r requirements.txt -c requirements-constraints.txt \
    && pip uninstall --yes setuptools \
    && find /usr /opt -type f -iname 'setuptools-*.whl' -delete \
    && python -c 'import importlib.util; assert importlib.util.find_spec("setuptools") is None, "setuptools must not be present in the runtime image"'

RUN python -c 'import cairosvg; png = cairosvg.svg2png(bytestring=b"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"2\" height=\"2\"><rect width=\"2\" height=\"2\" fill=\"#00549f\"/></svg>"); assert png.startswith(b"\x89PNG\r\n\x1a\n")'

RUN groupadd --system --gid 10001 meeting \
    && useradd --system --uid 10001 --gid meeting --home-dir /app --no-create-home meeting \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R meeting:meeting /app

COPY --chown=meeting:meeting . .

COPY --chmod=755 docker/entrypoint.sh /usr/local/bin/meeting-entrypoint

USER meeting

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/meeting-entrypoint"]
