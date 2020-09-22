def get_jsonp_dict(callback_name, jsonp_data):
    null = None
    true = True
    false = False
    dicts = {}

    def callback(json):
        dicts.update(json)

    jsonp_data = jsonp_data.replace(callback_name, 'callback')
    exec(jsonp_data)  # 把其它函数名变成callback()函数，再执行
    return dicts
