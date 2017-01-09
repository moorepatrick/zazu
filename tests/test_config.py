# -*- coding: utf-8 -*-
import click
import git
import os
import pytest
import yaml
import tempfile
import zazu.config

__author__ = "Nicholas Wiles"
__copyright__ = "Copyright 2016"


@pytest.fixture()
def git_repo():
    dir = tempfile.mkdtemp()
    repo = git.Repo.init(dir)
    readme = os.path.join(dir, 'README.md')
    with open(readme, 'w'):
        pass
    repo.index.add([readme])
    repo.index.commit('initial readme')
    return repo


@pytest.fixture()
def repo_with_teamcity(git_repo):
    root = git_repo.working_tree_dir
    teamcity_config = {
        'ci': {
            'type': 'TeamCity',
            'url': 'http://teamcity.lily.technology:8111/'
        }
    }
    with open(os.path.join(root, 'zazu.yaml'), 'a') as file:
        file.write(yaml.dump(teamcity_config))
    return git_repo


@pytest.fixture()
def repo_with_invalid_ci(git_repo):
    root = git_repo.working_tree_dir
    teamcity_config = {
        'ci': {
            'type': 'foobar',
        }
    }
    with open(os.path.join(root, 'zazu.yaml'), 'a') as file:
        file.write(yaml.dump(teamcity_config))
    return git_repo


@pytest.fixture()
def repo_with_jira(git_repo):
    root = git_repo.working_tree_dir
    jira_config = {
        'issueTracker': {
            'type': 'Jira',
            'url': 'https://lily-robotics.atlassian.net/',
            'project': 'STI',
            'component': 'Zazu'
        }
    }
    with open(os.path.join(root, 'zazu.yaml'), 'a') as file:
        file.write(yaml.dump(jira_config))
    return git_repo


def test_teamcity_config(repo_with_teamcity):
    cfg = zazu.config.Config(repo_with_teamcity.working_tree_dir)
    tc = cfg.continuous_integration()
    assert tc is not None
    assert tc.type() == 'TeamCity'


def test_invalid_ci(repo_with_invalid_ci):
    cfg = zazu.config.Config(repo_with_invalid_ci.working_tree_dir)
    with pytest.raises(click.ClickException):
        cfg.continuous_integration()


def test_jira_config(repo_with_jira):
    cfg = zazu.config.Config(repo_with_jira.working_tree_dir)
    tracker = cfg.issue_tracker()
    assert tracker is not None
    assert tracker.type() == 'Jira'
