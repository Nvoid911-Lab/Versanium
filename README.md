# Versanium

## Purpose

Versanium is an Android browser project focused on providing a comfortable and consistent browsing experience across both smartphones and desktop-style environments.

## Relationship to Titanium Browser

Versanium is an independent, unofficial derivative of [Titanium Browser for Android](https://github.com/jqssun/android-titanium-browser). It inherits substantial architecture, functionality, patches, build-system work, and extension support from Titanium Browser and its upstream projects.

Versanium is not an official Titanium Browser release and is not maintained, endorsed, or supported by the upstream Titanium Browser developers. The project does not attempt to replace Titanium Browser; it explores additional improvements for specific Android usage scenarios, including smartphone and desktop-style environments such as Samsung DeX.

## Project repositories and development status

- Primary / Source of Truth: [Nvoid911-Lab/Versanium](https://github.com/Nvoid911-Lab/Versanium)
- Secondary / backup: [Nvoid911/Versanium](https://github.com/Nvoid911/Versanium)
- [Issues](https://github.com/Nvoid911-Lab/Versanium/issues)
- [Pull requests](https://github.com/Nvoid911-Lab/Versanium/pulls)
- [Build workflows](https://github.com/Nvoid911-Lab/Versanium/actions/workflows/build.yml)

Versanium is currently under Test validation. No production release is authorized. Experimental Test APKs may be produced only from explicitly reviewed project revisions and should not be treated as production releases.

Current Test builds target `arm64-v8a` and use the test package identity `io.github.nvoid911.versanium.test`. Production identity and release policy remain separate decisions.

For the current implementation and validation state, use the repository's open pull requests and issues rather than relying on historical build runs or old development branches.

## Features and project focus

Versanium-specific work includes features and fixes intended to improve browsing across smartphone and desktop-style Android environments. Current project areas include fullscreen behavior, independent smartphone/desktop-environment zoom handling, zoom settings portability, extension popup behavior in desktop mode, and media/Picture-in-Picture reliability.

Some features remain experimental or under validation. Their presence in source or a Test build does not imply that they are production-ready.

## Extensions

Versanium inherits extension support from Titanium Browser. Titanium Extension for Android is an upstream component and is not developed by Versanium:

- [Titanium Extension for Android](https://github.com/jqssun/android-titanium-extension)

Extension compatibility and behavior may vary by build and Android environment. Only install extensions you trust.

## Upstream and Credits

Versanium is based on the work of several upstream open-source projects. Special thanks and credit go to:

- [Titanium Browser for Android](https://github.com/jqssun/android-titanium-browser)
- [Vanadium](https://github.com/GrapheneOS/Vanadium)
- [Chromium](https://www.chromium.org/)

The original authors and contributors retain credit for their respective work. Upstream copyright notices, license notices, and attribution remain applicable to the portions of the project derived from their respective sources.

Where appropriate, changes developed in Versanium that may also benefit Titanium Browser can be considered separately for upstream contribution.

## License

Versanium is distributed under the applicable open-source licenses inherited from its upstream projects. The main project license is the GNU General Public License version 2 (GPLv2).

See the [`LICENSE`](LICENSE) file and individual source files for the full licensing and copyright information.

## Disclaimer

Versanium is provided as-is, without any guarantee of availability, compatibility, stability, or fitness for a particular purpose.

Some features may behave differently from upstream Titanium Browser. Versanium-specific bugs or regressions should not automatically be attributed to Titanium Browser or its developers.
