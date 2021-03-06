# -*- coding: utf-8 -*-
"""github functions for zazu"""
import click
import getpass
import github
import keyring
import re
import requests
import socket
import zazu.util

__author__ = "Nicholas Wiles"
__copyright__ = "Copyright 2016"


def get_gh_token():
    """Make new GitHub token"""
    api_url = 'https://api.github.com'
    add_auth = {
        "scopes": [
            "repo"
        ],
        "note": "zazu for {}@{}".format(getpass.getuser(), socket.gethostname())
    }
    token = None
    while token is None:
        user = zazu.util.prompt("GitHub username", expected_type=str)
        password = click.prompt("GitHub password", type=str, hide_input=True)
        r = requests.post('{}/authorizations'.format(api_url), json=add_auth, auth=(user, password))
        if r.status_code == 401:
            if 'Must specify two-factor authentication OTP code.' in r.json()['message']:
                headers = {'X-GitHub-OTP': click.prompt('GitHub two-factor code (6 digits)', type=str)}
                r = requests.post('{}/authorizations'.format(api_url), headers=headers, json=add_auth, auth=(user, password))
            else:
                click.echo("Invalid username or password!")
                continue
        if r.status_code == 201:
            token = r.json()['token']
        elif r.status_code == 422:
            click.echo('You already have a GitHub token for zazu in GitHub but it is not saved in the keychain! '
                       'Go to https://github.com/settings/tokens to generate a new one with "repo" scope')
            token = zazu.util.prompt('Enter new token manually')
        else:
            raise Exception("Error authenticating with GitHub, status:{} content:{}".format(r.status_code, r.json()))
    return token


def make_gh():
    token = keyring.get_password('https://api.github.com', 'token')
    if token is None:
        click.echo("No saved GitHub token found in keychain, lets add one...")
        token = get_gh_token()
        keyring.set_password('https://api.github.com', 'token', token)
    gh = github.Github(token)
    return gh


def parse_github_url(url):
    """Parses github url into organization and repo name"""
    tokens = re.split('/|:', url.replace('.git', ''))
    repo = tokens.pop()
    organization = tokens.pop()
    return organization, repo
