# Versanium

> Current checkpoint — 2026-10-28 JST: Brave #36838 Phase 1 source implementation
> is complete. **Phase 1 implemented but NOT compiled/built/device-verified.**
> Next: `READY_FOR_36838_PHASE1_PREBUILD_REVIEW`. A separate Source-of-Truth gate
> is required before GN/build. Java-only, Chrome-only, exact HTTPS mobile YouTube
> watch/fullscreen scope; #33522/#39765 remain unimplemented; old candidates stay
> retired. Zoom inputs and existing lifecycle statements are unchanged.
> This supersedes the retirement-only/current-no-port notices below, which remain
> historical. No saved Run9 access/change, GN/build/Actions/APK/merge/release/tag/
> Production operation or PR body edit occurred.
> See [implementation, verification and limits](docs/versanium/brave-36838-phase1/implementation.md).


> Current policy — 2026-10-28 JST: the former Versanium YouTube PiP,
> Diagnostics/unsafe diagnostics and Background candidates are **retired / superseded**.
> Their generators, runtime plumbing, dedicated apply controllers and tests are removed.
> Earlier candidate descriptions below and existing docs/versanium reports/manifests/logs
> are historical evidence, not current functionality or executable instructions.
> Zoom (phone/DeX, transfer, persistence, policy, backup), F11/display, branding,
> Chromium156 pins and non-PiP features remain unchanged. Saved generated source
> and existing APKs are untouched and still reflect their historical configuration.
> Future PiP work is limited to Brave #36838 (YouTube PiP lifecycle/dismiss),
> #33522 (background playback), #39765 (Chromium153+ screen-lock/onStop).
> No Brave code is ported here. Build/GN/Actions/APK/merge/release/tag/Production
> are prohibited in this cleanup phase; PR5 stays Draft/Open/unmerged, body unchanged.
> See [retirement plan and integrity ledger](docs/versanium/pip-candidate-retirement-2026-10-28/plan.md).
> Next: `READY_FOR_BRAVE_36838_33522_39765_READONLY_PORT_ANALYSIS`.


## Purpose

Versanium is an Android browser project focused on providing a comfortable and consistent browsing experience across both smartphones and desktop-style environments.

## Relationship to Titanium Browser

Versanium is built on top of Titanium Browser for Android and therefore inherits much of its architecture, functionality, and upstream work. The project does not attempt to replace Titanium Browser, but to explore additional improvements for specific Android usage scenarios.

## Project repositories and current builds

- Primary / Source of Truth: [Nvoid911-Lab/Versanium](https://github.com/Nvoid911-Lab/Versanium).
- Secondary / backup: [Nvoid911/Versanium](https://github.com/Nvoid911/Versanium).
- [Current project status](https://github.com/Nvoid911-Lab/Versanium/blob/migration/versanium/PROJECT_STATUS.md) and [Versanium issue tracker](https://github.com/Nvoid911-Lab/Versanium/issues).

Versanium is currently in Test validation. No production release is authorized. Test APKs are distributed as **Versanium-Test** artifacts of explicitly approved manual [Versanium Build runs](https://github.com/Nvoid911-Lab/Versanium/actions/workflows/build.yml), rather than promoted to production Releases.

The recorded successful [155-series IdeaPad recovery run](https://github.com/Nvoid911-Lab/Versanium/actions/runs/39765620887) reused its preserved source. It does not contain the new 156-series candidates under review. Device testing confirmed F11, and continued YouTube PiP/background issues on the smartphone while DeX worked.

The next review targets **156.0.8078.47**. Its expected Test filename is `Versanium-156.0.8078.47_Test.apk`; this is not a claim that the APK has already been built. Use the reviewed migration/feature revision only after explicit build authorization. Do not resume the old 155 tree as if it included new patches.

Test builds target `arm64-v8a` and use `io.github.nvoid911.versanium.test`, separate from Titanium F11 Test (`io.github.nvoid911.titanium.f11test`). An existing old APK retains its original identity. Production identity remains a separate deferred decision.

Download only the intended Test artifact from this project's successful run and check its source revision before installing. Report Versanium-specific problems in this project's issue tracker.

## Unofficial Project Notice

Versanium is an independent, unofficial derivative of Titanium Browser for Android. It is not an official Titanium Browser release and is not maintained, endorsed, or supported by the upstream Titanium Browser developers.

## Upstream and Credits

Versanium is based on the work of several upstream open-source projects.

Special thanks and credit go to:

- [Titanium Browser for Android](https://github.com/jqssun/android-titanium-browser)
- [Vanadium](https://github.com/GrapheneOS/Vanadium)
- [Chromium](https://www.chromium.org/)

Versanium inherits significant portions of its architecture, functionality, patches, and build system from these upstream projects and their contributors.

The original authors and contributors retain credit for their respective work.

Where appropriate, changes developed in Versanium that may also benefit Titanium Browser can be considered separately for upstream contribution.

## License

Versanium is distributed under the applicable open-source licenses inherited from its upstream projects.

The main project license is the GNU General Public License version 2 (GPLv2).

See the [`LICENSE`](LICENSE) file and individual source files for the full licensing and copyright information.

Upstream copyright notices, license notices, and attribution remain applicable to the portions of the project derived from their respective sources.

## Disclaimer

Versanium is provided as-is, without any guarantee of availability, compatibility, stability, or fitness for a particular purpose.

Some features may be experimental and may behave differently from upstream Titanium Browser.

Versanium-specific bugs or regressions should not automatically be attributed to Titanium Browser or its developers.

Users are responsible for evaluating whether a particular build is suitable for their own devices and use cases.
