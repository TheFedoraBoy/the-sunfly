# The Sunfly

A small newspaper site for one longform political essay a day. Django, Postgres, hosted on Railway.

Readers get four pages: today's essay, past essays, contributors, and about. You get a newsroom at `/admin/` where you create contributor profiles (name, title, photo, biography) and publish essays. Contributors are profiles only; they do not log in.

## Run it on your machine

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo       # optional: placeholder essays so pages aren't empty
python manage.py runserver
```

The site is at http://127.0.0.1:8000 and the newsroom at http://127.0.0.1:8000/admin/. Locally it uses SQLite, so there is nothing else to install.

Run the tests with `python manage.py test`.

## Put it on Railway

1. Push this folder to a GitHub repository.
2. In Railway, create a project from that repository.
3. Add a Postgres database to the same project.
4. Add a Volume to the web service, mounted at `/data`. Uploaded photos live here. **Without the volume, every photo disappears on the next deploy.**
5. On the web service, set these variables (also listed in `.env.example`):

   | Variable | Value |
   | --- | --- |
   | `SECRET_KEY` | A long random string. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
   | `MEDIA_ROOT` | `/data/media` |
   | `ADMIN_USERNAME` | Your newsroom login name |
   | `ADMIN_PASSWORD` | A strong password |

6. Generate a public domain for the web service (Settings, Networking).
7. Deploy. `railway.json` tells Railway to run migrations, collect static files, create your login, and start the server.
8. Open `https://your-domain/admin/` and log in.

After your first login, change your password in the newsroom and delete `ADMIN_PASSWORD` from Railway. The login is only created if it doesn't exist, so removing the variable is safe.

### Using your own domain

Add the domain in Railway, then set `ALLOWED_HOSTS` to it, comma separated and without `https://`, for example `thesunfly.com,www.thesunfly.com`.

## Using the newsroom

**Contributors.** Add a person with a name, title, photo and biography. Square photos work best. Photos are shown in blue duotone to match the paper; a profile with no photo shows the Sunfly bug.

**Essays.** Write the headline, optional subheading, pick the contributor, and write the body in Markdown:

| You type | Readers see |
| --- | --- |
| A blank line | A new paragraph |
| `## Heading` | A section heading |
| `> Text` | A pull quote |
| `*text*` / `**text**` | Italic / bold |
| `[words](https://link)` | A link |
| `---` | A dotted divider |

Set **Status** to Published and it goes live. Things worth knowing:

- The home page shows the newest published essay. It is labelled "Today's essay" if its date is today, otherwise "Latest essay", so a missed day doesn't leave the front page empty.
- A published essay with a future date stays hidden until that day. Use this to queue essays ahead.
- "Today" rolls over at midnight Eastern. Change it with the `TIME_ZONE` variable.
- Drafts and scheduled essays are visible to you while logged in, through the Preview link in the essay list.
- One essay per day is a convention, not a hard rule. The newsroom warns you if two are published for the same date.

**Site settings.** The tagline and the About page text.

## What's where

```
sunfly/            project settings and top-level URLs
paper/             the app: models, newsroom (admin.py), views, RSS feed, tests
templates/         page templates
static/paper/      stylesheet, the Sunfly logo (sunfly.svg), fonts
railway.json       Railway start command and health check
```

Fonts (Bowlby One, Fraunces) are bundled under the SIL Open Font License, so the site makes no requests to Google or anyone else.

## Limits

- Uploaded images are served by Django from the Railway volume. That is fine for a small readership. If traffic grows, move media to object storage (S3 or Cloudflare R2) with `django-storages`.
- Because of the volume, the web service runs as a single instance.
- Essay text is trusted and rendered without sanitising, since only newsroom logins can write it. Revisit that before ever accepting text from the public.
- There is no search, tagging, or comments.
