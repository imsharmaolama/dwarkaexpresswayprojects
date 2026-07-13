# Railway deployment config for the CMS admin server (cms.py).
# Vercel serves the static site; Railway runs the Python CMS that publishes to it.
# Deploy: New Project -> Deploy from GitHub repo (imsharmaolama/dwarkaexpresswayprojects)
#        -> Railway auto-detects Procfile (web: python cms.py)
# Env vars to set in Railway dashboard:
#   CMS_PW      = (your admin password; defaults to cms123 if unset)
#   GIT_NAME    = (git user.name for publish commits, e.g. DEP CMS)
#   GIT_EMAIL   = (git user.email for publish commits)
#   GITHUB_TOKEN= (a GitHub PAT with repo scope, so Publish can push)
# Railway assigns PORT automatically; cms.py binds 0.0.0.0:$PORT.
