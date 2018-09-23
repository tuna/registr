
initCardReader = ($requestBtn, callback) => {
    if(navigator.usb === undefined)
        return;

    var port;
    var decoder = new TextDecoder('gbk');

    function processText(text) {
        console.log(text);
        var content = text.match(/CardBegin([\s\S]+?)CardEnd/m);
        if (content && content.length > 1) {
            var stuNum = content[1].match(/StuNumber=(\w*)/);
            var name = content[1].match(/Name=(.*)/);
            var gender = content[1].match(/Gender=(\d?)/);
            console.log(stuNum[1]);
            console.log(name[1]);
            console.log(gender[1]);
            var numGender = parseInt(gender[1])%2;
            var strGender = isNaN(numGender) ? 'unknown' : ['女','男'][numGender];

            callback(stuNum[1], name[1], strGender)
        }
    }

    function connect() {
        console.log('Connecting to ' + port.device_.productName + '...');
        port.connect().then(() => {
            console.log(port);
            console.log('Connected.');
            port.onReceive = data => {
                try {
                    var text = decoder.decode(data);
                    processText(text);
                } catch (error) {
                    console.log('Process error: ' + error);
                }
            }
            port.onReceiveError = error => {
                console.log('Receive error: ' + error);
            };
        }, error => {
            console.log('Connection error: ' + error);
        });
    };


    $requestBtn.on('dblclick', function () {
        if (port) {
            // port.disconnect();
        } else {
            serial.requestPort().then(selectedPort => {
                port = selectedPort;
                connect();
            }).catch(error => {
                console.log('Connection error: ' + error);
            });
        }
    });

    serial.getPorts().then(ports => {
        if (ports.length == 0) {
            console.log('No devices found.');

            serial.requestPort().then(selectedPort => {
                port = selectedPort;
                connect();
            }).catch(error => {
                console.log('Connection error: ' + error);
            });

        } else {
            port = ports[0];
            connect();
        }
    });
};