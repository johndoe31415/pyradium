FROM node:22-alpine

RUN apk update && apk upgrade
RUN apk add git bash curl grep

#ENV DEBIAN_FRONTEND noninteractive
#ENV TERM xterm-256color
#RUN apt-get update && apt-get dist-upgrade --yes 
#RUN apt-get install --yes npm git curl


ENV SHELL /bin/bash
ENV PNPM_HOME /usr/bin
RUN curl -fsSL https://get.pnpm.io/install.sh | bash -

WORKDIR /
RUN git clone https://github.com/mathjax/MathJax-src.git mathjax

WORKDIR /mathjax
RUN git checkout 844ad7513005fa096a07d2468bf59c7f6a6c3a50
RUN npm install
RUN npm run --silent compile
RUN npm run --silent make-components
RUN npm link

WORKDIR /
RUN git clone https://github.com/mathjax/MathJax-demos-node.git mathjax-demos
WORKDIR /mathjax-demos
RUN npm install

COPY mjrender /mjrender
WORKDIR /mjrender
RUN npm install
