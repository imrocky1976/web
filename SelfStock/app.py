from flask import Flask, render_template, jsonify
import datetime
import urllib

stock_data = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = datetime.timedelta(seconds=10)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list=<codes>', methods=['GET'])
def query(codes):
    req = urllib.request.Request('http://hq.sinajs.cn/list=%s' % codes)
    res = urllib.request.urlopen(req)
    if res.status != 200 and res.reason != 'OK':
        return ''
    data = res.read().decode('gbk')
    res.close()
    print(data)
    return data

@app.route('/parse/<id>', methods=['GET'])
def parse(id):
    print("recv id:", id)
    first_char = id[0]
    result = []
    if first_char.isdigit():
        #result = [i[0:2] for i in stock_data if i[0].startswith(id)]
        for i in stock_data:
            if i[0].startswith(id):
                result.append({'code': i[0], 'name': i[1], 'py': i[2]})
                if len(result) >= 10:
                    break
    else:
        for i in stock_data:        
            if i[2].startswith(id):
                result.append({'code': i[0], 'name': i[1], 'py': i[2]})
                if len(result) >= 10:
                    break
    print('return data:', result)
    return jsonify({'data': result})

if __name__ == '__main__':
    with open('stocks.csv', 'rt', encoding='gbk') as f:
        stock_data = f.readlines()
        stock_data = [i.split() for i in stock_data]

    #print(stock_data)                
    app.run(debug=True, host='127.0.0.1', port=7000)