// Called when the user clicks on the browser action.
chrome.browserAction.onClicked.addListener(function(tab) {
  chrome.tabs.executeScript(
      null, {code:"document.body.style.background='red !important'"});
});

chrome.tabs.onActivated.addListener(function(activeInfo) {
	chrome.tabs.getSelected(null, function(tab) {
        var tabUrl = tab.url;
        send(localStorage['exttype'] + "|" + tabUrl);
	});
});

//--------------------- WEBSOCKETS -----------------------
var socket = null;
var WEBSCK_ADDY = "ws://localhost:8081/test";

function send(val) {
  if (!socket) {console.log('Not connected'); return;}
  socket.send(val);
  console.log('> ' + val);
}

function connect() {
  if ('WebSocket' in window) {
    socket = new WebSocket(WEBSCK_ADDY);
  } else if ('MozWebSocket' in window) {
    socket = new MozWebSocket(WEBSCK_ADDY);
  } else {
    return;
  }

  socket.onopen = function () {
    console.log('Opened');
  };
  socket.onmessage = function (event) {
    console.log(event.data);
  };
  socket.onerror = function () {
    console.log('Error');
  };
  socket.onclose = function (event) {
    var logMessage = 'Closed (';
    if ((arguments.length == 1) && ('CloseEvent' in window) &&
        (event instanceof CloseEvent)) {
      logMessage += 'wasClean = ' + event.wasClean;
      // code and reason are present only for
      // draft-ietf-hybi-thewebsocketprotocol-06 and later
      if ('code' in event) {
        logMessage += ', code = ' + event.code;
      }
      if ('reason' in event) {
        logMessage += ', reason = ' + event.reason;
      }
    } else {
      logMessage += 'CloseEvent is not available';
    }
    console.log(logMessage + ')');
  };
}

function closeSocket() {
  if (!socket) {console.log('Not connected'); return;}
  socket.close();
}

function websocket_init() {
  if ('MozWebSocket' in window) {
    console.log('Use MozWebSocket');
  } else if (!('WebSocket' in window)) {
    console.log('WebSocket is not available');
  }
  connect();
}
websocket_init();