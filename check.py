# -- coding: utf-8 --
import math
from flask import Flask, request, render_template, jsonify, Response, redirect
import json
import time
from urllib import parse
from DBconnect import MysqlHelp


check_user = Flask(__name__)
mysqlhelp = MysqlHelp('127.0.0.1', 'root', '', 'Douyu')


@check_user.route("/")
def hello():
        return render_template("index.html")


@check_user.route("/dyapi/check", methods=["POST", "GET"])
def check():
    return_method_error = {'error': '1', 'info': 'method error!'}
    if request.method == "GET":
        return Response(json.dumps(return_method_error, ensure_ascii=False), mimetype='application/json')
    # 默认返回内容
    return_dict = {'error': '0', 'info': '操作成功', 'msg': 'error', 'tips': '声明\n'
                                                                      '1.本作者提供的脚本可能存在有不完善之处，如果在使用中如发现BUG，请及时提交与作者(邮箱：262325005@qq.com)，本作者将尽力修改完善之。\n'
                                                                      '2.该脚本是完全开源且免费提供给大家，请勿用于商业用途或是不合法用途。\n'
                                                                      '3.该脚本会收集所需要的用户信息，此举为了帮助开发者改进程序为您提供更好的体验，并不会对账户安全造成威胁。\n'
                                                                      '同意请“确认”，不同意请“取消”。\n'}
    ret = request.form.to_dict()
    if ret.get('uid') == '' or ret.get('nickname') == '' or ret.get('is_fans') == '':
        return_dict['error'] = '1'
        return_dict['info'] = '操作失败'
        return_dict['msg'] = '请求参数错误！'
        return Response(json.dumps(return_dict, ensure_ascii=False), mimetype='application/json')

    uid = ret.get('uid')
    name = ret.get('nickname')
    is_fans = ret.get('is_fans')
    c_name = parse.unquote(name)
    run_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
    create_log_table(uid)
    return_dict['msg'] = check_this(uid, c_name, is_fans, run_time)
    return Response(json.dumps(return_dict, ensure_ascii=False), mimetype='application/json')


@check_user.route("/dyapi/delete", methods=["POST", "GET"])
def delete():
    return_method_error = {'error': '1', 'info': 'method error!'}
    if request.method == "GET":
        return Response(json.dumps(return_method_error, ensure_ascii=False), mimetype='application/json')
    # 默认返回内容
    return_dict = {'error': '0', 'info': '操作成功', 'msg': 'error'}
    ret = request.form.to_dict()
    if ret.get('uid') == '':
        return_dict['error'] = '1'
        return_dict['info'] = '操作失败'
        return_dict['msg'] = '请求参数错误！'
        return Response(json.dumps(return_dict, ensure_ascii=False), mimetype='application/json')

    uid = ret.get('uid')
    return_dict['msg'] = delete_this(uid)
    return Response(json.dumps(return_dict, ensure_ascii=False), mimetype='application/json')


@check_user.route("/dyapi/insert_log", methods=["POST", "GET"])
def insert():
    return_method_error = {'error': '1', 'info': 'method error!'}
    if request.method == "GET":
        return Response(json.dumps(return_method_error, ensure_ascii=False), mimetype='application/json')
    # 默认返回内容
    return_dict = {'error': '0', 'info': '操作成功', 'msg': ''}
    print(request.form)
    ret = request.form.to_dict()
    if ret.get('uid') == '' or ret.get('gid') == '' or ret.get('rid') == '' or ret.get('gift_time') == '':
        return_dict['error'] = '1'
        return_dict['info'] = '操作失败'
        return_dict['msg'] = '请求参数错误！'
        return Response(json.dumps(return_dict, ensure_ascii=False), mimetype='application/json')

    uid = ret.get('uid')
    gift_id = ret.get('gid')
    room_id = ret.get('rid')
    gift_time = ret.get('gift_time')
    nn = ret.get('nn')
    return_dict['msg'] = insert_log(uid, gift_id, room_id, gift_time, nn)
    return Response(json.dumps(return_dict, ensure_ascii=False), mimetype='application/json')


@check_user.route("/dyapi/query_log", methods=["GET", "POST"])
def query():
    return_dict = {'error': '0', 'info': '查询成功', 'list': ''}
    if request.method == "POST":
        ret = request.form.to_dict()
        uid = ret.get("uid")
        return_dict['list'] = query_log(uid)
        currentpage = int(ret.get('currentpage'))
        return_dict['list'] = return_dict['list'][15 * (currentpage - 1):15 * currentpage]
        return Response(json.dumps(return_dict, ensure_ascii=False), mimetype='application/json')
    ret = request.args.to_dict()
    if ret.get('uid') == '' or len(ret) == 0:
        return_dict['error'] = '1'
        return_dict['info'] = '操作失败'
        return Response(json.dumps(return_dict, ensure_ascii=False), mimetype='application/json')

    ban_uid_list = ReadBanTxt('ban.txt')
    uid = ret.get('uid')
    user_name = query_user(uid)
    currentpage = ret.get('currentpage')
    if user_name != '':
        return_dict['list'] = query_log(uid)
        length = len(return_dict['list'])
        totalpage = math.ceil(length/15)
    else:
        return_dict['error'] = '1000'
        return_dict['info'] = '用户不存在！'
        return Response(json.dumps(return_dict, ensure_ascii=False), mimetype='application/json')
    if uid in ban_uid_list:
        return render_template("ban.html")
    if currentpage is None or currentpage == '' or currentpage == '1':
        currentpage = 1
        return_dict['list'] = return_dict['list'][0:15]
    else:
        currentpage = int(ret.get('currentpage'))
        return_dict['list'] = return_dict['list'][15*(currentpage-1):15*currentpage]
    return render_template("test.html", x=return_dict, name=user_name, currentpage=currentpage, totalpage=totalpage, length=length)


def ReadBanTxt(rootdir):
    lines = []
    with open(rootdir, 'r') as file_to_read:
        while True:
            line = file_to_read.readline()
            if not line:
                break
            line = line.strip('\n')
            lines.append(line)
    return lines


def create_log_table(uid):
    mysqlhelp.insert_delete_update('create table if not exists gift_log_'+uid+'(id int(10) auto_increment primary key, uid varchar(30), gift_name varchar(50), room_id varchar(30), get_time varchar(100), nn varchar(100))')


def insert_log(uid, gift_id, room_id, gift_time, nn):
    # create table gift_log (id int(10) auto_increment primary key, uid varchar(30), gift_name varchar(50), room_id varchar(30), get_time varchar(100))
    time_Array = time.localtime(int(gift_time[:10]))
    Style_Time = time.strftime("%Y-%m-%d %H:%M:%S", time_Array)
    print(Style_Time)
    gift_name = ''
    if gift_id == '974':
        gift_name = "办卡"
    elif gift_id == '975':
        gift_name = "大气"
    elif gift_id == '978':
        gift_name = "666"
    elif gift_id == '979':
        gift_name = "飞机"
    elif gift_id == '981':
        gift_name = "火箭"
    mysqlhelp.insert_delete_update('insert into gift_log_'+uid+'(uid, gift_name, room_id,get_time, nn) values (%s, %s, %s, %s, %s)', [uid, gift_name, room_id, Style_Time, nn])
    mysqlhelp.insert_delete_update("insert into gift_log(uid, gift_name, room_id,get_time, nn) values (%s, %s, %s, %s, %s)", [uid, gift_name, room_id, Style_Time, nn])
    return "success"


def query_user(uid):
    values = mysqlhelp.select_fetchall('select * from dy_user where uid = %s', (uid,))
    if len(values) == 0:
        return ""
    else:
        return values[0][1]


def query_log(uid):
    values = mysqlhelp.select_fetchall('select * from gift_log_' + uid + ' where uid = %s', (uid,))
    values.reverse()
    return values


def delete_this(uid):
    mysqlhelp.insert_delete_update('delete from dy_user where uid = %s', [uid])
    mysqlhelp.insert_delete_update('drop table if exists gift_log_'+uid)
    return "success"


def check_this(uid, name, is_fans, run_time):
    # create table dy_user (uid varchar(20) primary key, nickname varchar(20), is_fans varchar(20), last_time varchar(50))
    values = mysqlhelp.select_fetchall('select * from dy_user where uid = %s', [uid])
    if len(values) == 0:
        insert_user(uid, name, is_fans, run_time)
        return "error"
    else:
        if values[0][1] != name or values[0][2] != is_fans:
            update_user(uid, name, is_fans)
        elif values[0][3] != run_time:
            update_time(uid, run_time)
        return "success"


def insert_user(uid, name, is_fans, run_time):
    mysqlhelp.insert_delete_update('insert into dy_user (uid, nickname, is_fans, last_time) values (%s, %s, %s, %s)', [uid, name, is_fans, run_time])


def update_user(uid, name ,is_fans):
    mysqlhelp.insert_delete_update('update dy_user set nickname = %s, is_fans = %s where uid = %s', [name, is_fans, uid])


def update_time(uid, run_time):
    mysqlhelp.insert_delete_update('update dy_user set last_time = %s where uid = %s', [run_time, uid])


if __name__ == "__main__":
    check_user.run(debug=True)
