## Requirements

- Python 3
- Phabricator API Token
- Slack slash intergration

## Install

```shell
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
export PHAB_URL=<phabricator_url>
export PHAB_TOKEN=<phabricator_api_token>
export SLASH_TOKEN=<slash_token>
gunicorn --reload main:__hug_wsgi__
```

## Syntax

```
/[slash_command] [action] [options]
```

## Actions

### Get list of tasks
- `action` can be `q`, `query` or `search`
- `options` :
  - `me` or `mine` : Your tasks (same username of Phabricator)
  - `open`, `resolved`, `invalid`, `wontfix` or `spite` : status of task

## Examples :

- `/phab q open` : Get open tasks
- `/phab q me open` : Get your open tasks
- `/phab query mine resolved` : Get your resolved tasks