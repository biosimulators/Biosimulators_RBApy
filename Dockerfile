FROM python:3.9-slim-buster

ARG VERSION="0.0.2"
ARG SIMULATOR_VERSION="1.0.2"

# metadata
LABEL \
    org.opencontainers.image.title="RBApy" \
    org.opencontainers.image.version="${SIMULATOR_VERSION}" \
    org.opencontainers.image.description="Package for automated generation of bacterial Resource Balance Analysis (RBA) models and simulation of RBA models" \
    org.opencontainers.image.url="https://sysbioinra.github.io/RBApy/" \
    org.opencontainers.image.documentation="https://sysbioinra.github.io/RBApy/" \
    org.opencontainers.image.source="https://github.com/biosimulators/Biosimulators_RBApy" \
    org.opencontainers.image.authors="BioSimulators Team <info@biosimulators.org>" \
    org.opencontainers.image.vendor="BioSimulators Team" \
    org.opencontainers.image.licenses="GPL-3.0-or-later" \
    \
    base_image="python:3.9-slim-buster" \
    version="${VERSION}" \
    software="RBApy" \
    software.version="${SIMULATOR_VERSION}" \
    about.summary="Package for automated generation of bacterial Resource Balance Analysis (RBA) models and simulation of RBA models" \
    about.home="https://sysbioinra.github.io/RBApy/" \
    about.documentation="https://sysbioinra.github.io/RBApy/" \
    about.license_file="https://github.com/SysBioInra/RBApy/blob/master/LICENSE.txt" \
    about.license="SPDX:GPL-3.0-or-later" \
    about.tags="systems biology,biochemical networks,Resource Balance Analysis,RBA,SED-ML,COMBINE,OMEX,BioSimulators" \
    maintainer="BioSimulators Team <info@biosimulators.org>"

# Install GLPK
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        gcc \
        libglpk-dev \
    && pip install glpk \
    && apt-get remove -y \
        gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# fonts for matplotlib
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Install RBApy
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        git \
    \
    && cd /tmp \
    && git clone https://github.com/biosimulators/RBApy.git \
    && pip install RBApy/[glpk,gurobi] \
    \
    && rm -r RBApy \
    && apt-get remove -y \
        git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy code for command-line interface into image and install it
COPY . /root/Biosimulators_RBApy
RUN pip install /root/Biosimulators_RBApy[glpk,gurobi] \
    && rm -rf /root/Biosimulators_RBApy
ENV VERBOSE=0 \
    MPLBACKEND=PDF
RUN mkdir -p /.config/matplotlib \
    && mkdir -p /.cache/matplotlib \
    && chmod ugo+rw /.config/matplotlib \
    && chmod ugo+rw /.cache/matplotlib \
    && python -c "import matplotlib.font_manager"

# Entrypoint
ENTRYPOINT ["biosimulators-rbapy"]
CMD []
