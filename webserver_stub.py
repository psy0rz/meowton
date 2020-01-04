#!/usr/bin/env python3


from bottle import route, run, template, static_file


@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='micropython/static')


run(host='localhost', port=8080, reloader=True)
