from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
 
app = Flask(__name__)
api = Api(app)
 
STOCK_LIST = {
    's_sh000001': 'var hq_str_s_sh000001="上证指数,2876.4009,7.3514,0.26,1189311,11952877";',
    's_sz399001': 'var hq_str_s_sz399001="深证成指,9069.83,-108.949,-1.19,135170367,13998323";',
    's_sz399006': 'var hq_str_s_sz399006="创业板指,1553.78,-7.474,-0.48,11259100,1618374";',
    'sh600000': 'var hq_str_sh600000="浦发银行,10.260,10.170,10.020,10.270,10.020,10.020,10.040,14707431,149389344.000,152880,10.020,179200,10.010,399100,10.000,51400,9.990,49500,9.980,73515,10.040,44700,10.050,8832,10.060,10000,10.070,10100,10.080,2018-08-01,14:25:46,00";',
    'sz000002': 'var hq_str_sz000002="万 科Ａ,23.240,23.320,22.410,23.240,22.210,22.410,22.450,61670113,1395506424.860,3100,22.410,69095,22.400,4500,22.390,10600,22.380,2300,22.370,6500,22.450,11804,22.460,38500,22.470,13700,22.480,17500,22.490,2018-08-01,14:26:06,00";'
}
 
from functools import wraps
from flask import make_response


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun

parser = reqparse.RequestParser()
parser.add_argument('id', type=str)
parser.add_argument('value', type=str)
 
def abort_if_not_exist(user_id):
    if user_id not in STOCK_LIST:
        abort(404, message="User {} doesn't exist".format(user_id))
 
class Stock(Resource):
    @allow_cross_domain
    def get(self, stock_id):
        abort_if_not_exist(stock_id)
        return STOCK_LIST[stock_id]

    @allow_cross_domain
    def delete(self, stock_id):
        abort_if_not_exist(stock_id)
        del STOCK_LIST[stock_id]
        return '', 204
 
    @allow_cross_domain
    def put(self, stock_id):
        args = parser.parse_args(strict=True)
        STOCK_LIST[args['id']] = args['value']
        return STOCK_LIST[args['id']], 201


class StockList(Resource):
    @allow_cross_domain
    def get(self):
        return STOCK_LIST
 
    @allow_cross_domain
    def post(self):
        args = parser.parse_args(strict=True)
        STOCK_LIST[args['id']] = args['value']
        return STOCK_LIST[args['id']], 201
 
api.add_resource(StockList, '/list')
api.add_resource(Stock, '/list=<path:stock_id>')
 
if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)


