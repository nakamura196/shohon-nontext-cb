# frozen_string_literal: true

source 'https://rubygems.org'

# needed for Jekyll
gem 'jekyll'
gem 'webrick'
gem 'logger'
gem 'base64'
gem 'ostruct'

# needed for Rake tasks
gem 'rake'
gem 'csv'
gem 'fileutils'
gem 'mini_magick'
unless Gem.win_platform?
  gem 'image_optim'
  gem 'image_optim_pack'
end

# Japanese/Chinese/Korean search index, built at build time (see cjk_index in _config.yml)
group :jekyll_plugins do
  # Gemfile.lock is not committed in this repo; 1.x releases keep the index format and API
  gem 'cjk_index', '~> 1.1', require: 'cjk_index/jekyll'
  # static IIIF: info.json and the item manifests at build time (see static_iiif: in _config.yml)
  gem 'static_iiif', git: 'https://github.com/nakamura196/static_iiif.git', ref: 'c2806f1464483a0fbcaf992a6b434a69bca53a9a', require: 'static_iiif/jekyll'
end

# modern / museum looks and the light/dark switch (see the theme's README)
gem 'cb-museum-theme', git: 'https://github.com/nakamura196/cb-museum-theme.git', ref: 'a4aa7f07e1e7b751602c3c390c7b2f3c4b626497'
