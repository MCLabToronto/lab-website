---
title: People
nav:
  order: 3
  tooltip: Meet our team
---

# {% include icon.html icon="fa-solid fa-users" %} People

The MCLab brings together researchers and trainees with diverse backgrounds, expertise, and perspectives.

<div style="max-width: 500px; margin: 30px auto;">
  <img
    src="{{ 'images/team.JPG' | relative_url }}"
    alt="MCLab team"
    style="width: 100%; height: auto; border-radius: 4px;"
  >
</div>

{% include section.html %}

## Lab Head

{% include list.html data="members" component="portrait" filter="role == 'pi'" %}

## Postdoctoral Fellows

{% include list.html data="members" component="portrait" filter="role == 'postdoc'" %}

## PhD Students

{% include list.html data="members" component="portrait" filter="role == 'phd'" %}

## Master's Students

{% include list.html data="members" component="portrait" filter="role == 'master'" %}

## Research Staff

{% include list.html data="members" component="portrait" filter="role == 'staff'" %}