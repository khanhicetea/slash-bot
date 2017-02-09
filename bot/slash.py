import os
import json
from datetime import datetime
from .phabricator import Phabricator
import requests
import random


EPHEMERAL = "ephemeral"
IN_CHANNEL = "in_channel"
PHAB_URL = os.environ.get('PHAB_URL')
PHAB_TOKEN = os.environ.get('PHAB_TOKEN')
TASK_PRIORITY_EMOJI = {
    'pink': ':sos:',
    'violet': ':busts_in_silhouette:',
    'red': ':bangbang:',
    'orange': ':exclamation:',
    'yellow': ':warning:',
    'sky': ':raising_hand:'
}
TASK_STATUES = ['open', 'resolved', 'invalid', 'wontfix', 'spite']
DEPLOY_USER = os.environ.get('DEPLOY_USER')
DEPLOY_PASSWORD = os.environ.get('DEPLOY_PASSWORD')
DEPLOY_URL = os.environ.get('DEPLOY_URL')
DEPLOY_PROJECT_ID = os.environ.get('DEPLOY_PROJECT_ID')
DEPLOY_TEMPLATE_IDS = os.environ.get('DEPLOY_TEMPLATE_IDS')
phabricator = Phabricator(PHAB_URL, PHAB_TOKEN)

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y") if timestamp else ''

def format_task(task):
    return u"- {emoji} [<{link}|{tid}>] @{owner} - {title}".format(
        link=task['uri'],
        tid=task['objectName'],
        emoji=TASK_PRIORITY_EMOJI[task['priorityColor']],
        title=task['title'],
        owner=(task['owner']['userName'] if task['owner'] else 'Nobody'))

def sort_tasks(tasks):
    items = {key: [] for key in TASK_PRIORITY_EMOJI.keys()}
    sorted_tasks = []

    for task in tasks:
        items[task['priorityColor']].append(task)
    for p in ['pink', 'violet', 'red', 'orange', 'yellow', 'sky']:
        sorted_tasks += items[p]

    return sorted_tasks

def get_users(args):
    result = phabricator.run('user.query', args)

    return {user['phid']: user for user in result}

def get_user_by_username(user_name):
    result = phabricator.run('user.query', {'usernames': [user_name]})

    return result[0] if result else None

def get_tasks(args):
    result = phabricator.run('maniphest.query', args)
    tasks = sort_tasks(result.values())

    owner_phids = [task['ownerPHID'] for task in tasks if task['ownerPHID']]
    owners = get_users({'phids': owner_phids})

    for task in tasks:
        task['owner'] = owners[task['ownerPHID']] if task['ownerPHID'] else None
    
    return tasks

def slash_main(user_name, text):
    cmd, *params = text.split(' ')

    if cmd in ['deploy']:
        template_id = 0
        for temp in DEPLOY_TEMPLATE_IDS.split(','):
            parts = temp.split(':')
            if parts[0] == params[0]:
                template_id = int(parts[1])
        if template_id:
            s = requests.Session()
            r = s.post('{}/api/auth/login'.format(DEPLOY_URL), json={
                "auth": DEPLOY_USER,
                "password": DEPLOY_PASSWORD
            })
            if r.status_code == 204:
                r = s.post('{}/api/project/{}/tasks'.format(DEPLOY_URL, DEPLOY_PROJECT_ID), json={
                    "template_id": template_id,
                    "debug": False,
                    "dry_run": False
                })
                if r.status_code == 201:
                    return "Roger that !!! :ok_hand: I'm going to deploy `{}` ... Get a :beers: plz !".format(params[0]), IN_CHANNEL
        return "Oops, you're drunk, man ! Something went wrong  ... :scream_cat:", IN_CHANNEL
    elif cmd in ['random', 'say']:
        r = requests.get('http://quotes.stormconsultancy.co.uk/random.json')
        result = r.json()
        return "`{}` - {}".format(result['quote'], result['author']), IN_CHANNEL
    elif cmd in ['vietlott']:
        numbers = ['`{}`'.format(x if x > 9 else '0' + str(x)) for x in random.sample(range(1, 45), 6)]
        return ":joy: Ra đê sớm nha pồ : {}".format(' '.join(numbers)), IN_CHANNEL
    elif cmd in ['q', 'query', 'search']:
        args = {}
        if 'me' in params or 'mine' in params:
            current_user = get_user_by_username(user_name)
            if current_user:
                args['ownerPHIDs'] = [current_user['phid']]
            else:
                return "Username {} is not found in Phabricator, please use the same username".format(user_name), EPHEMERAL
        for status in TASK_STATUES:
            if status in params:
                args['status'] = 'status-{}'.format(status)
        
        tasks = get_tasks(args)
        rows = [format_task(task) for task in tasks]
        return "\n".join(rows), EPHEMERAL

    return "{} said `{}`".format(user_name, text), EPHEMERAL
