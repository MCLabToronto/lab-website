# Research framework maintenance

The five themes, their accessible/mobile text, colors and future links live in `_data/research_themes.json`.

To activate a theme, set its `url` to an existing site-relative destination, for example `/projects/example/`. Keep `url` as an empty string until the destination is ready. The corresponding polygon on desktop and heading on mobile will become keyboard-accessible links automatically. Never use `#` as a placeholder.

`points` contains polygon coordinates in the original image's 1637 × 961 coordinate system. The central title is excluded from all clickable regions. If replacing the image, update these coordinates to match it. Changes to theme text also require updating the image; the JSON supplies the screen-reader and mobile version.

The figure is the previously approved color proposal. On small screens (900px or less), semantic color cards replace the bitmap to keep the text readable. No project links are enabled initially.
