# Versanium supplied-logo assets

The inline logo was visually supplied in chat, but its original PNG bytes are not available in this workspace. No replacement logo has been generated or substituted.

Once the original PNG is provided as a file, run:

    python tools/versanium/generate_icons.py /path/to/original.png

The script preserves master.png byte-for-byte, creates standard/adaptive/monochrome density resources from the same artwork, and exports repository, social-preview (PNG + SVG source), and fastlane assets. Only transparency extraction, padding, and resizing are used for the logo. Social-preview text is separate from the logo.

Review all outputs before committing assets. The build preflight deliberately fails until assets.json and every digest-checked output exist. No old Titanium icon or generated approximation is accepted as a substitute. GitHub social preview must be uploaded separately through repository settings; creating the asset does not set the hosted preview.
