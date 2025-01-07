import json
import os
import time

import requests
from github import Github, Auth
from github.GithubException import GithubException
from config import settings
from loguru import logger

g = Github(
    auth=Auth.AppAuth(settings.app_id,
                      settings.app_private_key
                      ).get_installation_auth(settings.app_installation_id))

source_branch = "main"


def any_plugin(raw_plugin_json, plugin_json):
    mew_plugin_json = []
    flag = False
    for plugin in raw_plugin_json:
        if plugin["Id"] == plugin_json["Id"]:
            mew_plugin_json.append(plugin_json)
            flag = True
        else:
            mew_plugin_json.append(plugin)
    if not flag:
        mew_plugin_json.append(plugin_json)
    return flag, mew_plugin_json


def get_pr_file(plugin_json_url, assets):
    resp = requests.get(plugin_json_url)
    resp.raise_for_status()
    plugin_json = resp.json()
    plugin_json["Assets"] = assets
    return plugin_json


def create_pr(assets):
    plugin_json_url = None
    logo_url = None
    logo_name = None
    new_assets = []
    for asset in assets:
        if asset["content_type"].startswith("image/"):
            logo_url = asset["browser_download_url"]
            logo_name = asset["name"]
        elif asset["name"] == "plugin.json":
            plugin_json_url = asset["browser_download_url"]
        else:
            new_assets.append({
                "id": asset["id"],
                "name": asset["name"],
                "content_type": asset["content_type"],
                "size": asset["size"],
                "created_at": asset["created_at"],
                "updated_at": asset["updated_at"],
                "browser_download_url": asset["browser_download_url"],
            })
    if plugin_json_url is None:
        logger.warning("No plugin json file found, skip")
        return
    new_branch = str(int(time.time()))
    logger.info(f"[{new_branch}]Creating new branch")
    repo = g.get_repo(settings.repo_name)
    plugin_file = repo.get_contents("plugin.json")
    raw_plugin_json = json.loads(plugin_file.decoded_content.decode("utf-8"))
    plugin_json = get_pr_file(plugin_json_url, new_assets)
    plugin_id = plugin_json["Id"]
    plugin_version = plugin_json["Version"]
    source_ref = repo.get_git_ref(f"heads/{source_branch}")
    new_branch_ref = repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=source_ref.object.sha)
    if logo_url:
        logo_flag = False
        logo_path = f"{plugin_id}/{logo_name}"
        logo_data = {
            "path": logo_path,
            "message": f"{'Update' if logo_flag else 'Create'} Plugin Logo: {plugin_id} v{plugin_version}",
            "content": requests.get(logo_url).content,
        }
        try:
            logo_file_content = repo.get_contents(logo_path)
            logo_flag = True
        except GithubException:
            pass
        except Exception as e:
            logger.error(e)

        if logo_flag:
            repo.update_file(**logo_data,
                             sha=logo_file_content.sha,
                             branch=new_branch)
        else:
            repo.create_file(**logo_data, branch=new_branch)
        logger.info(f"[{new_branch}]Creating Logo")
        plugin_json[
            "Logo"] = f"https://raw.githubusercontent.com/{settings.repo_name}/refs/heads/main/{logo_path}"
    flag, mew_plugin_json = any_plugin(raw_plugin_json, plugin_json)
    commit_message = f"{'Update' if flag else 'Create'} Plugin: {plugin_id} v{plugin_version}"

    repo.update_file("plugin.json", commit_message,
                     json.dumps(mew_plugin_json, indent=4, ensure_ascii=False),
                     sha=plugin_file.sha,
                     branch=new_branch)

    logger.info(f"[{new_branch}]Update Plugin json")
    pr_body = "..."
    pr = repo.create_pull(
        title=commit_message,
        body=pr_body,
        head=new_branch,
        base=source_branch
    )
    logger.info(f"[{new_branch}]Create Pr")
    pr.merge()
    logger.info(f"[{new_branch}]Merge Pr")
    new_branch_ref.delete()