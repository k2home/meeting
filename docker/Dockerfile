FROM python:3.13-slim

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
    && apt-get install -y --no-install-recommends libcairo2 postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-constraints.txt ./
RUN python -m pip install --upgrade pip 'setuptools>=78.1.1' \
    && pip install -r requirements.txt -c requirements-constraints.txt \
    && python -c 'import importlib.metadata as metadata, pathlib, shutil; version = metadata.version("setuptools"); assert tuple(int(part) for part in version.split(".")[:2]) >= (78, 1), version; roots = (pathlib.Path("/usr/local/lib/python3.13/site-packages"), pathlib.Path("/usr/lib/python3/dist-packages"), pathlib.Path("/usr/lib/python3.13/site-packages")); [shutil.rmtree(path) for root in roots if root.exists() for path in root.glob("setuptools-*.dist-info") if path.name != f"setuptools-{version}.dist-info"]'

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
