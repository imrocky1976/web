
function updateStocks() {
    //alert('This pops up every 5 seconds and is annoying!');
    var table = document.getElementById("tblStocks");
    for (var i = 0; i < table.rows.length; i++) {
        row = table.rows[i];
        if (row.cells[1].innerHTML == "代码")
            continue;
        else {
            var code = row.cells[1].innerHTML;
            //alert(code);
            updateStock(code, row);
        }
    }
}

function updateStock(code, trow) {
    var real_code = null;
    if (code == '000001') {
        real_code = 's_sh000001';
    } else if (code == '399001') {
        real_code = 's_sz399001';
    } else if (code == '399006') {
        real_code = 's_sz399006';
    } else if (String(code).charAt(0) == '6') {
        real_code = "sh" + code;
    } else {
        real_code = "sz" + code;
    }
        
    var xhr = new XMLHttpRequest();
    //xhr.open("GET", "http://hq.sinajs.cn/list=" + real_code, true);
    xhr.open("GET", document.URL + "list=" + real_code, true);
    //xhr.setRequestHeader('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0');
    //xhr.send(JSON.stringify({
    //    value: 'value'
    //}));
    xhr.onreadystatechange = function() {//服务器返回值的处理函数，此处使用匿名函数进行实现
        if(xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200){
            var responseText = xhr.responseText;
            if (responseText == 'var hq_str_sys_auth="FAILED";') {
                return;
            }
            if (responseText == '') {
                return;
            }

            var elements = responseText.split(',');
            var curPrice, curChange;
            if (code == '000001' || code == '399001' || code == '399006') {
                curPrice = parseFloat(elements[1]).toFixed(2);
                curChange = parseFloat(elements[3]).toFixed(2);

            } else {
                curPrice = parseFloat(elements[3]).toFixed(2);
                curChange = (((elements[3] - elements[2]) / elements[2]) * 100).toFixed(2);
            }

            trow.cells[0].innerHTML = elements[0].split('"')[1];
            trow.cells[1].innerHTML = code;
            trow.cells[2].innerHTML = curPrice;
            if (curChange > 0.0) {
                trow.cells[3].innerHTML = "+" + curChange + "%";
                setClass(trow.cells[3], 'red');
            } else {
                trow.cells[3].innerHTML = curChange + "%";
                if (curChange < 0.0) {
                    setClass(trow.cells[3], 'green');
                } else {
                    setClass(trow.cells[3], 'grey');
                }
            }
        }
    };
    xhr.send();
}

function setClass(cell, className) {
    cell.className = className;
}

function addStocks(codes) {
    for (var i = 0; i < codes.length; i++) { 
        var table = document.getElementById("tblStocks");
        var lastRow = table.rows[table.rows.length-1];  
        var newRow = lastRow.cloneNode(true);      
        newRow.cells[0].innerHTML = "";
        newRow.cells[1].innerHTML = codes[i];
        newRow.cells[2].innerHTML = 0;
        newRow.cells[3].innerHTML = 0;
        table.appendChild(newRow);        
    }
}

function addStock(event) {
    code = document.getElementsByName('stock-search-text')[0].value;
    // TODO 验证代码是否有效
    var table = document.getElementById("tblStocks");
    var lastRow = table.rows[table.rows.length-1];  
    var newRow = lastRow.cloneNode(true);      
    newRow.cells[0].innerHTML = "";
    newRow.cells[1].innerHTML = code;
    newRow.cells[2].innerHTML = 0;
    newRow.cells[3].innerHTML = 0;
    table.appendChild(newRow);
    updateStock(code, newRow);        
}

function parseInput() {
    // 清空提示列表
    var t =  document.getElementById("tblSearch");
    for (var i = t.rows.length - 1; i >= 0; i--) {
        t.deleteRow(i);
    }
    
    // 请求提示信息
    id = document.getElementsByName('stock-search-text')[0].value;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", document.URL + 'parse/' + id, true);
    xhr.onreadystatechange = function() {
        if(xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200){
            var responseText = xhr.responseText;
            if (responseText == '') {
                return;
            }
            parsedStocks = JSON.parse(responseText);
            //alert(parsedStocks);
            var data = parsedStocks['data'];
            for (var i = 0; i <  data.length; i++) {
                //alert(data[i])
                var r = t.insertRow();
                r.insertCell().innerHTML = data[i]['code'];
                r.insertCell().innerHTML = data[i]['name'];
                r.insertCell().innerHTML = data[i]['py'];
                r.onmouseover = rowHighlight;
                r.onclick = rowSeclect;
            }
        }
    };
    xhr.send();
}

function initStocks() {
    var codes = ['600000', '000002', '300146'];
    addStocks(codes);
    updateStocks();
}

setInterval(updateStocks, 5000); // Time in milliseconds


function rowHighlight() {
    var tbl = document.getElementById("tblSearch");
    var trs = tbl.rows;
    for (var i = 0; i < trs.length; i++) {
        if (trs[i] == this) {
            trs[i].style.background = "yellow";
        }
        else {
            trs[i].style.background = "white";
        }
    }
}

function rowSeclect(event) {
    document.getElementsByName('stock-search-text')[0].value = this.cells[0].innerHTML;
}