# Optional standalone image for the BASH Consultants Jekyll site.
#
# Day-to-day development uses docker-compose.yml (plain ruby:3.3 image with the
# repo bind-mounted; no build step needed). This Dockerfile exists for the rare
# case where you want a self-contained image — CI smoke tests, hosting the dev
# server without a checkout, etc.
#
# NOTE: the Gemfile expects the jekyll-theme-zer0 checkout at /zer0-mistakes
# (override with ZER0_MISTAKES_PATH). Mount it at runtime, same as compose does:
#
#   docker build -t bashconsultants .
#   docker run -p 4042:4042 \
#     -v /path/to/zer0-mistakes:/zer0-mistakes:ro \
#     bashconsultants

FROM ruby:3.4

WORKDIR /app

COPY . /app

# bundle install runs at container start (CMD below), not at build time: the
# Gemfile's jekyll-theme-zer0 path gem resolves against the runtime mount, which
# does not exist while the image is building.

EXPOSE 4042

CMD ["bash", "-c", "bundle install && bundle exec jekyll serve --host 0.0.0.0 --port 4042 --config '_config.yml,_config_dev.yml'"]
