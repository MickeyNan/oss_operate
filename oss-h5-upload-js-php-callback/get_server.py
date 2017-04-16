import time
import datetime
import json
import base64
import hmac
from hashlib import sha1 as sha
from tornado import httpserver
from tornado import gen
import tornado.ioloop
import tornado.options
import tornado.web
import hashlib
from tornado.options import define, options
from concurrent.futures import ThreadPoolExecutor

accessKeyId = '6MKOqxGiGU4AUk44'
accessKeySecret = 'ufu7nS8kS59awNihtjSonMETLI0KLy'
host = 'http://post-test.oss-cn-hangzhou.aliyuncs.com'
expire_time = 30  
upload_dir = 'user-dir/'
callback_url = "http://oss-demo.aliyuncs.com:23450";


thread_pool = ThreadPoolExecutor(2)

define("port", default=8002, help="run on the given port", type=int)



def get_iso_8601(expire):
    print expire
    gmt = datetime.datetime.fromtimestamp(expire).isoformat()
    gmt += 'Z'
    return gmt

@gen.coroutine
def get_token():
    now = int(time.time())
    expire_syncpoint  = now + expire_time
    expire = yield thread_pool.submit(get_iso_8601,expire_syncpoint)

    policy_dict = {}
    policy_dict['expiration'] = expire
    condition_array = []
    array_item = []
    array_item.append('starts-with');
    array_item.append('$key');
    array_item.append(upload_dir);
    condition_array.append(array_item)
    policy_dict['conditions'] = condition_array 
    policy = json.dumps(policy_dict).strip()
    #policy_encode = base64.encodestring(policy)
    policy_encode = base64.b64encode(policy)
    print policy_encode 
    h = hmac.new(accessKeySecret, policy_encode, sha)
    sign_result = base64.encodestring(h.digest()).strip()

    callback_dict = {}
    callback_dict['callbackUrl'] = callback_url;
    callback_dict['callbackBody'] = 'filename=${object}&size=${size}&mimeType=${mimeType}&height=${imageInfo.height}&width=${imageInfo.width}';
    callback_dict['callbackBodyType'] = 'application/x-www-form-urlencoded';
    callback_param = json.dumps(callback_dict).strip()
    base64_callback_body = base64.b64encode(callback_param);


    token_dict = {}
    token_dict['accessid'] = accessKeyId
    token_dict['host'] = host
    token_dict['policy'] = policy_encode
    token_dict['signature'] = sign_result 
    token_dict['expire'] = expire_syncpoint
    token_dict['dir'] = upload_dir
    token_dict['callback'] = base64_callback_body

    #web.header('Content-Type', 'text/html; charset=UTF-8')
    result = json.dumps(token_dict)
    raise gen.Return(result)

class TokenRequestHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        token = yield get_token()
        self.set_header("Access-Control-Allow-Methods","POST,GET")
        self.set_header("Access-Control-Allow-Origin","*")
        self.write(token)


def main():
    application = tornado.web.Application([
        (r"/token", TokenRequestHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
