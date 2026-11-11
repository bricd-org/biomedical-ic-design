---
title: References
nav_order: 7
permalink: /references/
---

# References

This list is kept in [`_data/references.yml`](https://github.com/bricd-org/biomedical-ic-design/blob/main/_data/references.yml); the numbers in the text are positions in that file.

<ol class="references">
{%- for r in site.data.references %}
  <li id="ref-{{ r.key }}">{{ r.text | markdownify | remove: "<p>" | remove: "</p>" | strip }}</li>
{%- endfor %}
</ol>
