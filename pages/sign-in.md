---
title: Sign in
description: Sign in to the BASH Consulting platform from one page that lists each hosted application and links to that application's own secure sign-in
author: Amr Abdel-Motaleb
layout: default
slug: sign-in
permalink: /sign-in/
date: 2026-11-28T12:00:00.000Z
lastmod: 2026-11-28T12:00:00.000Z
draft: false
# Left out of the sitemap while no application is open (docs/sign-in.md).
sitemap: false
keywords:
  - BASH Consulting sign in
  - platform sign in
  - client portal
  - zer0-CMS sign in
  - passkey sign in
  - single sign-on
---

{% assign open_services = site.data.platform.services | where: "enabled", true %}

## Choose where to sign in

{% if open_services.size > 0 %}
Each application signs you in on its own address, with a [passkey](https://fidoalliance.org/passkeys/), a one-time code or your organization's single sign-on. BASH Consulting never asks for your password on this page.

<div class="list-group my-4">
  {% for service in open_services %}
  <a class="list-group-item list-group-item-action d-flex justify-content-between align-items-start gap-3" href="https://{{ service.host }}{{ service.sign_in }}" rel="noopener">
    <span>
      <span class="fw-bold d-block">Sign in to {{ service.title }}</span>
      <span>{{ service.summary }}</span>
    </span>
    <span class="badge text-bg-secondary">{{ service.host }}</span>
  </a>
  {% endfor %}
</div>
{% else %}
No application is open for sign-in yet. When one is, it is listed here with a link to its own sign-in, which uses a [passkey](https://fidoalliance.org/passkeys/), a one-time code or your organization's single sign-on.
{% endif %}

## Check the address before you sign in

Every BASH sign-in address starts with `https://` and ends in `bash-365.com`. This page only links to those addresses. If a page anywhere else asks for your BASH sign-in, close it and [tell us](/contact/).

## Ask for access

Access is by invitation. [Book a free consultation](/contact/) to ask about it.
