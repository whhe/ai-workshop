# Upstream Repository Resolution

Remote names (`origin`, `upstream`, `fork`, etc.) are only hints — never assume a specific name maps to the true upstream. Apply this decision order:

1. If the user gave an explicit GitHub issue or pull request URL, or `owner/repo`, use it directly (derive `owner/repo` from the URL when needed).
2. List all configured remotes (`git remote -v`) and resolve each URL to `owner/repo`.
3. Determine the current user's GitHub login via `gh api user --jq .login`. If `gh` is unavailable or unauthenticated, **stop here for login** — do not guess login from env vars or URLs. Continue to step 4 with login **unknown**.
4. Pick the upstream by remote count (and login, when known):
   - **1 remote** → use it as upstream.
   - **2 remotes** → if login is **known** and exactly one remote's `owner` equals that login, pick the *other* remote (fork heuristic). If login is **unknown**, or zero or two remotes would match that login, present both `owner/repo` candidates and ask which is upstream — do not infer fork direction from remote *names* alone.
   - **≥3 remotes** → present candidates; ask the user which is upstream; do not proceed until confirmed.
5. Record the chosen `owner/repo` and use it for all subsequent steps.
