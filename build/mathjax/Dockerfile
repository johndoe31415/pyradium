FROM ubuntu:24.04

ENV DEBIAN_FRONTEND noninteractive
ENV TERM xterm-256color
RUN apt-get update && apt-get dist-upgrade --yes 
RUN apt-get install --yes npm git

WORKDIR /
RUN git clone https://github.com/mathjax/MathJax.git mathjax

WORKDIR /mathjax
RUN git checkout 4.0.0-beta.7
RUN npm install && npm run build || true
