# Deploying WEMS live on PythonAnywhere (free tier)

Puts the webapp on `https://YOURUSERNAME.pythonanywhere.com` with HTTPS and a
**persistent database** — the closest thing to running it on the office PC,
but reachable from anywhere. Deploys are a one-command `git pull` from this
GitHub repo.

> **First thing after going live: complete the setup wizard** (first visit
> redirects to it). It is one-time only — do it immediately before sharing
> the URL, so nobody else can claim the admin account.

## One-time setup (~15 minutes)

1. **Create the account** at [pythonanywhere.com](https://www.pythonanywhere.com)
   → "Create a Beginner account" (free). Your site will be
   `https://USERNAME.pythonanywhere.com`.

2. **Clone the repo** — open a **Bash console** and run:

   ```bash
   git clone https://github.com/xl8saif/WEMS.git ~/WEMS
   ```

3. **Create the virtualenv and install dependencies:**

   ```bash
   mkvirtualenv wems-env --python=$(which python3.10)
   pip install -r ~/WEMS/requirements.txt
   ```

4. **Restore your real data** — on the **Files** tab, upload the current
   `waraq.db` from the office PC into `home/USERNAME/WEMS/database/`.
   That single file carries all users (passwords are hashed), clients,
   jobs, invoices, and payments. *(This office PC keeps working offline as
   a backup instance — see "Two databases" below.)*

5. **Create the web app** — **Web** tab → *Add a new web app* →
   "Manual configuration" → **Python 3.10**.
   Then set, on the same tab:
   - **Source code directory:** `/home/USERNAME/WEMS`
   - **Virtualenv:** `/home/USERNAME/.virtualenvs/wems-env`
   - *(optional, faster pages)* **Static files** mapping:
     `/static/` → `/home/USERNAME/WEMS/static/`

6. **Point the WSGI file at the app** — on the **Web** tab open the
   *WSGI configuration file* link (`/var/www/USERNAME_pythonanywhere_com_wsgi.py`)
   and replace its body with:

   ```python
   import sys
   path = '/home/USERNAME/WEMS'
   if path not in sys.path:
       sys.path.insert(0, path)

   # Free accounts have no env-var panel, so set the secret here.
   # IMPORTANT: generate your own long random string — never reuse this one.
   import os
   os.environ['SECRET_KEY'] = 'PASTE-A-LONG-RANDOM-STRING-HERE'

   from wsgi import application
   ```

   Generate a random secret in any console:
   `python -c "import secrets; print(secrets.token_hex(32))"`

7. **Green Reload button** (Web tab) → open
   `https://USERNAME.pythonanywhere.com` → log in with a real account.
   Live. 🎉

## Updating the app after each `git push`

Open a Bash console on PythonAnywhere and run:

```bash
bash ~/WEMS/pa_update.sh
```

It pulls the latest code from GitHub, re-syncs dependencies only when
`requirements.txt` changed, and reloads the web app.

## Two databases — read this once

- **PythonAnywhere** = the live, shared instance for all 13 users.
- **This office PC** = a private offline copy. It will **diverge** from the
  live one as soon as both are used. Treat the live site as the source of
  truth, and periodically use the app's **Database Backup** page on the live
  site to download fresh `.db` copies onto the office PC.

## Security notes (already built in)

- Login now **locks a username for 10 minutes after 5 failed attempts**
  (per-username, because PythonAnywhere's proxy shares IPs).
- Passwords are stored as scrypt hashes — the `.db` file alone is not enough
  to read them.
- HTTPS is automatic on `*.pythonanywhere.com`.
- The database is **never** in the GitHub repo (`.gitignore` keeps it out) —
  only the code is public, not your business data.
