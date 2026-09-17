---
title: Team
nav:
  order: 3
  tooltip: Meet our team
---

The MCLab brings together researchers and trainees with diverse backgrounds, expertise, and perspectives.

{% include section.html %}

<h2 class="lab-team-heading">Lab Head</h2>

{% include list.html data="members" component="member-row" filter="role == 'pi' && group != 'alum' && group != 'alumni'" %}

<h2 class="lab-team-heading">Postdoctoral Fellows</h2>

{% include list.html data="members" component="member-row" filter="role == 'postdoc' && group != 'alum' && group != 'alumni'" %}

<h2 class="lab-team-heading">PhD Students</h2>

{% include list.html data="members" component="member-row" filter="role == 'phd' && group != 'alum' && group != 'alumni'" %}

<h2 class="lab-team-heading">Master's Students</h2>

{% include list.html data="members" component="member-row" filter="role == 'master' && group != 'alum' && group != 'alumni'" %}

<h2 class="lab-team-heading">Research Staff</h2>

{% include list.html data="members" component="member-row" filter="role == 'staff' && group != 'alum' && group != 'alumni'" %}

<h2 class="lab-team-heading">Alumni</h2>

{% include list.html data="members" component="member-row" filter="role == 'alumni' || group == 'alum' || group == 'alumni'" %}
