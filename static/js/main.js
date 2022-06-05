window.onload = () => {
    let csvFile;
    let dataTransfer;
    const uploadBox = document.querySelector('.upload-box');
    const fileName = document.querySelector('.file-name');

    const clearButton = document.getElementById("clearButton");
    const startButton = document.getElementById("startButton");
    const candleSize = document.getElementById("candle_size");

    const balance = document.getElementById("balance");
    const leverage = document.getElementById("leverage");
    const backtestResult = document.getElementById("backtest_result");

    uploadBox.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadBox.style.backgroundColor = '#3700b3';
    });

    uploadBox.addEventListener('dragleave', _ => {
        uploadBox.style.backgroundColor = '#6200ee';
    });

    uploadBox.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadBox.style.backgroundColor = '#6200ee';
        dataTransfer = e.dataTransfer;
        csvFile = dataTransfer.files[0];
        fileName.innerHTML = csvFile.name;
    });

    clearButton.onclick = _ => {
        if (dataTransfer != null) {
            dataTransfer.clearData();
        }
        csvFile = null;
        fileName.innerHTML = "";
    }

    startButton.onclick = _ => {
        if (csvFile == null) {
            alert('csv 파일을 선택한 후 사용해 주세요.');
        } else if (candleSize.options[candleSize.selectedIndex].value === "nop") {
            alert('캔들 크기를 선택해 주세요.');
        } else if (balance.value === 0) {
            alert('잔고를 입력해 주세요.');
        } else if (leverage.value === 0) {
            alert('레버리지 를 입력해 주세요.');
        } else {
            const fileReader = new FileReader();
            fileReader.onload = e => {
                let dataUrl = e.target.result;
                dataUrl = dataUrl.substring(dataUrl.indexOf(',') + 1, dataUrl.length);

                const message = document.createElement('h1');
                message.innerHTML = "백테스팅중..."
                backtestResult.innerHTML = ""
                backtestResult.appendChild(message);

                const param = {
                    'token': token,
                    'balance': balance.value,
                    'leverage': leverage.value,
                    'candleSize': candleSize.options[candleSize.selectedIndex].value,
                    'data': dataUrl
                };

                $.ajax({
                    type: 'POST',
                    url: '/trading_view/backtest/request',
                    data: JSON.stringify(param),
                    dataType: 'JSON',
                    contentType: 'application/json',
                    timeout: 60000,
                    success: result => {
                        let col = ['항목', '결과'];
                        let table = document.createElement('table');
                        let tr = table.insertRow(-1);

                        for (let i = 0; i < col.length; i++) {
                            let th = document.createElement('th')
                            th.innerHTML = col[i];
                            tr.appendChild(th);
                        }

                        for (let key in result) {
                            tr = table.insertRow(-1);
                            let tableCell = tr.insertCell(-1);
                            tableCell.innerHTML = key
                            tableCell = tr.insertCell(-1);
                            tableCell.innerHTML = result[key];
                        }

                        backtestResult.innerHTML = "";
                        backtestResult.appendChild(table);
                        alert('백테스팅이 완료 되었습니다!')
                    },
                    error: (request, status, error) => {
                        alert("오류 : " + status + " / " + error);
                        backtestResult.innerHTML = "";
                    }
                });
            }
            fileReader.onerror = ex => {
                alert('파일을 읽어들이는데 실패하였습니다. 다시 시도해 주세요.');
            }

            fileReader.readAsDataURL(csvFile);
        }
    }
}
