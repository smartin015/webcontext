
chrome.tabs.onActivated.addListener(function(activeInfo) {
	chrome.tabs.getSelected(null, function(tab) {
        var tabUrl = tab.url;
        sendURL(tabUrl);
	});
});

chrome.tabs.onUpdated.addListener(function(tabID, changeInfo, tab) {
  if (changeInfo.hasOwnProperty('url'))
    sendURL(changeInfo['url']);
});

function getHost(href) {
  var l = document.createElement("a");
  l.href = href;
  return l.hostname;
}

//--------------------- WEBSOCKETS -----------------------
var socket = null;
var WEBSCK_ADDY = "ws://"+localStorage["server_url"]+":8081/test";
var blacklist = ['chrome-extension://', 'newtab', 'chrome-devtools://', 'chrome://'];

function sendURL(url) {
  if (!socket) {console.log('Not connected'); return;}
  for (i in blacklist)
      if (url.indexOf(blacklist[i]) != -1)
        return;
  socket.send(localStorage['exttype'] + "|" + url);
  console.log('> ' + localStorage['exttype'] + "|" + url);
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
    if (localStorage["exttype"] == "server")
      return;
    
    var url = decodeURIComponent(event.data);
    
    //Skip erroneous requests to snap to chrome extension stuff
    for (i in blacklist)
      if (url.indexOf(blacklist[i]) != -1)
        return;
      
    var querystr =  url.split("?")[0] + "*";
    console.log("Searching for " + querystr);
    chrome.tabs.query({"url": querystr}, function (matchtabs) {
      if (matchtabs.length > 0) {
        chrome.tabs.move(matchtabs[0].id, {'index': 0});
        chrome.tabs.update(matchtabs[0].id, {'active': true});
      }
      else
        chrome.tabs.create({url: decodeURIComponent(event.data)});
    });
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
    
    //Attempt to reconnect
    window.setTimeout(websocket_init, 5000);
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
