import json
import random

import bs4
import requests
from flask import request

from utils.decorators.check_sign import check_sign
from utils.exceptions import custom_abort
from . import api, config


@api.route("/auto/evaluate", methods=["GET"])
@check_sign(set())
def handle_auto_evaluate():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "DNT": "1",
        "Host": "zxpj.nuc.edu.cn",
        "Origin": "http://zxpj.nuc.edu.cn",
        "Referer": "http://zxpj.nuc.edu.cn/login",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,"
                      "likeGecko)Chrome/73.0.3683.86Safari/537.36"
    }
    Max = request.args.get('max', 100)
    Min = request.args.get('min', 95)
    name = request.args.get('name', type=str)
    passwd = request.args.get('passwd', '111111')
    session = requests.session()
    session.get(config.base_url)
    headers["Cookie"] = "shiroCookie=" + session.cookies["shiroCookie"]
    session.headers = headers
    session, res = login(session, name, passwd)
    if session:
        soup = bs4.BeautifulSoup(res, "html.parser")
        div = soup.find_all("div", class_="am-active")[0]
        xxqs = div.find_all(class_="xxq")
        if len(xxqs) < 1:
            custom_abort(-8, "任务已完成")
        i = 1
        for x in xxqs:
            commentary_course(session, x.string, Max, Min)
            i += 1
    return {
        "code": 0
    }


def login(session: requests.session, username: str, password: str) -> tuple:
    post_data = {
        "username": username,
        "password": password,
        "kaptcha": ""
    }
    html = session.post(config.login_url, data=post_data, timeout=5).content.decode("utf-8")
    if html.find(u"评课任务") != -1:
        return session, html
    elif html.find(u"账号密码错误") != -1:
        custom_abort(-3, "账号或密码错误")
    else:
        custom_abort(-3)


def commentary_course(session: requests.session, id_: str, Max: int, Min: int):
    base_url = "http://zxpj.nuc.edu.cn/evaluateRet/selectInfoByEid/" + id_
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "zxpj.nuc.edu.cn",
        "Referer": "http://zxpj.nuc.edu.cn/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/73.0.3683.86 Safari/537.36",
        "Cookie": "shiroCookie=" + session.cookies["shiroCookie"]}
    session.headers = headers
    r = session.get(base_url).content.decode("utf-8")
    soup = bs4.BeautifulSoup(r, "html5lib")
    eid = soup.find_all(id="eid")[0]["value"]
    trs = soup.find_all("tr")[1:-1]
    content = []
    for tr in trs:
        item = tr.find(class_="am-form-contentid")["value"]
        score = random.randint(Min, Max)
        content.append({int(item): score})
    info = {"content": content, "eid": eid, "summarize": "无"}
    info_json = json.dumps(info)
    session.headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8", "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "DNT": "1",
        "Host": "zxpj.nuc.edu.cn", "Origin": "http://zxpj.nuc.edu.cn",
        "Referer": "http://zxpj.nuc.edu.cn/evaluateRet/selectInfoByEid/104979",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/73.0.3683.86 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest", "Cookie": "shiroCookie=" + session.cookies["shiroCookie"]}
    session.post(config.post_url, data=info_json)
