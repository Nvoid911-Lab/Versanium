# IdeaPad Run #5 recovery

Status: proposed and locally checked; no recovery build has been run.

Use the existing **Versanium Build** workflow at the reviewed recovery revision:

- `runner_provider`: `ideapad`
- `f11_test_build`: `true`
- `resume_ideapad`: `true`

Do not rerun the historical Run #5. Do not run the original build.sh again against the prepared tree. Old revisions retain destructive checkout behavior.

Before dispatch, review/approve this change, complete the upstream/PiP review required by RULES, and start the existing IdeaPad runner. This change itself does not dispatch a build. The preserved original repository must still be at 6e7517e6de89e5a1230cebf906470795112466a3; do not git pull it. The workflow checks out new control code in its own child directory. Keep the terminal open and the PC awake during the authorized run.

The original 53GB Chromium tree stays in place, including its 14GB output. Recovery validates expected inputs and GN args, then runs chrome_java and chrome_public_apk incrementally. It does not install dependencies, use sudo, run gclient, reset source, reapply patches, or regenerate GN. It disables depot_tools self-update for this attempt. Changed/missing state stops recovery; it never silently falls back to full setup.

The timeout for recovery is 20 hours. No completion time is promised. Default compilation parallelism is retained; `IdeaPad-resume-resources` contains vmstat measurements for subsequent CPU/memory/swap tuning. Artifact `Versanium-Test` contains only the freshly signed arm64 Test APK, retained for seven days. Production remains blocked.

If validation fails, preserve the source and outputs and inspect the message. Do not delete state files, run git clean/reset, or change args.gn to bypass the guard. Empty current OOM logs do not rule out earlier memory pressure. Siso determines actual reusable work during the next authorized execution.

After recovery, review logs/telemetry and perform smartphone + DeX validation. General persistent-workspace provisioning, unattended dependency setup and source-update invalidation remain separate follow-up work. Review and synchronize Primary → Secondary without force before refreshing canonical Project Sources. No main branch change is required for this implementation: it adds an input to the already existing workflow file.
