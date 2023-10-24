import sys
import re
import os
from urllib import parse
from pyuque.client import Yuque
import requests
import time
from huepy import *
from prettytable import PrettyTable

# 定义Token(执行脚本时传递即可)
Token = sys.argv[1]

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "X-Auth-Token": Token
    }

# 获取仓库列表
def get_repos(user_id):
    repos = {}
    for repo in yuque.user_list_repos(user_id)['data']:
        repo_id = str(repo['id'])
        repo_name = repo['name']
        repos[repo_id] = repo_name
    return repos



def main():
    # 获取用户ID
    user_id = yuque.user.get()['data']['id']

    # 获取知识库列表
    all_repos = get_repos(user_id)
    
    # 遍历知识库字典，分别输出ID和文档名称
    for repo_id, repo_name in all_repos.items():
        print(f"{repo_id} : {repo_name}")



if __name__ == '__main__':
    token = Token
    yuque = Yuque(token)
    main()
