# Versanium supplied-logo assets

The actual attachment is a 1280×1280 JPEG, not a PNG. `master-original.jpg` preserves its exact bytes; `master.png` is a lossless format conversion of its decoded pixels. No logo was generated, traced or redesigned.

Regenerate with:

    python tools/versanium/generate_icons.py res/versanium/master-original.jpg

White artwork is extracted using luminance as alpha. Only JPEG near-black background noise (luminance <=16/255) is removed in the transparent foreground; the preserved original and canonical PNG are untouched. The full foreground fits within the adaptive 66dp circular safe zone. Five densities provide legacy 48dp icons, 108dp transparent foregrounds and black backgrounds. Existing resource names/GN entries are retained. The monochrome bitmap references the same white-alpha foreground.

`assets.json` checks all 24 outputs. Social preview PNG (1280×640) and SVG are ready for manual upload in GitHub repository Settings → Social preview; generating files does not set the hosted preview. Fastlane icon is 512×512 and feature graphic 1024×500. Text belongs to the surrounding layout, never to the original logo.
