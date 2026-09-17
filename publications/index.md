---
title: Publications
nav:
  order: 4
  tooltip: Browse our publications
---

# {% include icon.html icon="fa-solid fa-book-open" %} Publications

Publications are updated automatically from the Google Scholar profiles of MCLab members.

{% assign publications = site.data.citations | sort: "date" | reverse %}
{% assign current_year = "" %}

{% if publications.size == 0 %}

_No publications are currently available._

{% else %}

{% for publication in publications %}

  {% assign publication_year = publication.year | default: "Undated" %}

  {% if publication_year != current_year %}

    <h2>{{ publication_year }}</h2>

    {% assign current_year = publication_year %}

  {% endif %}

  <div class="citation-container">

    <div class="citation">

      <div class="citation-text">

        {% if publication.link %}

          <a
            href="{{ publication.link | xml_escape }}"
            class="citation-title"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ publication.title }}
          </a>

        {% else %}

          <span class="citation-title">
            {{ publication.title }}
          </span>

        {% endif %}

        {% if publication.authors.size > 0 %}

          <div class="citation-authors">
            {{ publication.authors | join: ", " }}
          </div>

        {% endif %}

        <div class="citation-details">

          {% if publication.publisher %}

            <span class="citation-publisher">
              {{ publication.publisher }}
            </span>

          {% endif %}

          {% if publication.publisher and publication_year %}

            &nbsp;·&nbsp;

          {% endif %}

          {% if publication_year %}

            <span class="citation-date">
              {{ publication_year }}
            </span>

          {% endif %}

        </div>

      </div>

    </div>

  </div>

{% endfor %}

{% endif %}
