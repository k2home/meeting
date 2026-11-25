ARG VCS_REF=unknown
ARG VCS_BRANCH=unknown
ARG VCS_COMMIT_DATE=unknown

FROM debian:trixie-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        libcairo2 \
        postgresql-client \
        python3.13 \
        python3.13-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-constraints.txt ./
RUN python3.13 -m venv /opt/venv \
    && /opt/venv/bin/python -m pip install --upgrade pip 'setuptools>=78.1.1' \
    && /opt/venv/bin/pip install -r requirements.txt -c requirements-constraints.txt \
    && /opt/venv/bin/pip uninstall --yes setuptools \
    && /opt/venv/bin/python -c 'import importlib.util; from importlib.metadata import distributions; assert importlib.util.find_spec("setuptools") is None, "setuptools module must not be present in the runtime environment"; assert not any((dist.metadata.get("Name") or "").lower() == "setuptools" for dist in distributions()), "setuptools metadata must not be present in the runtime environment"'

FROM debian:trixie-slim AS runtime

ARG VCS_REF=unknown
ARG VCS_BRANCH=unknown
ARG VCS_COMMIT_DATE=unknown

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH" \
    MEETING_BUILD_COMMIT=${VCS_REF} \
    MEETING_BUILD_COMMIT_DATE=${VCS_COMMIT_DATE} \
    MEETING_BUILD_BRANCH=${VCS_BRANCH}

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        libcairo2 \
        postgresql-client \
        python3.13 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

RUN python -c 'import cairosvg; png = cairosvg.svg2png(bytestring=b"<svg xmlns=\\"http://www.w3.org/2000/svg\\" width=\\"2\\" height=\\"2\\"><rect width=\\"2\\" height=\\"2\\" fill=\\"#00549f\\"/></svg>"); assert png.startswith(bytes([137, 80, 78, 71, 13, 10, 26, 10]))'

RUN groupadd --system --gid 10001 meeting \
    && useradd --system --uid 10001 --gid meeting --home-dir /app --no-create-home meeting \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R meeting:meeting /app

COPY --chown=meeting:meeting . .

COPY --chmod=755 docker/entrypoint.sh /usr/local/bin/meeting-entrypoint

USER meeting

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/meeting-entrypoint"]
