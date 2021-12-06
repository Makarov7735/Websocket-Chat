
const socket = new WebSocket('ws://127.0.0.1:9000')
      chat = document.querySelector('.chat-messeges')
      online = document.querySelector('#online-users')
      statusDiv = document.querySelector('.status')
      sendButton = document.querySelector('.send-btn');
let username;

 
function showConnectionStatus(data) {
    statusDiv.innerHTML = `Server status - ${data}`;
}

function showMessage(data) {
    let message = document.createElement('div');
    if (data['name'] == username) {
        message.innerHTML = '<b>You:</b> ' + data['data'] + '<div class="date">' + data['date'] + '</div>';
        message.className = 'message sender';
    } else {
        message.innerHTML = '<b>' + data['name'] + '</b>' + ': ' + data['data'] + '<div class="date">' + data['date'] + '</div>';
        message.className = 'message';
    }
    chat.append(message);
}

function showOnlineStatus(data) {
    online.innerHTML = `Online users - ${data}`
}

// login to server
socket.addEventListener('open', () => {
    showConnectionStatus('connected');
    while (!username) {
        username = prompt('Enter your usename');
    }

    let jsonData = JSON.stringify({'status': 'username', 'data': username});
    socket.send(jsonData);
});

// listen server
socket.addEventListener('message', event => {
    let data = JSON.parse(event.data);

    if (data['status'] == 'online') {
        showOnlineStatus(data['data'])
    } else if (data['status'] == 'message') {
        showMessage(data);
    }

    chat.scrollTop = chat.scrollHeight;
});

// if server closed
socket.addEventListener('close', () => {
    showConnectionStatus('disconnected');
    online.innerHTML = 'Online users - 0'
});

// send message
sendButton.addEventListener('click', () => {
    let data = document.querySelector('input').value;
    if (data.split(' ').join('')) {
        let jsonData = JSON.stringify({'status': 'message', 'data': data});
        socket.send(jsonData);
        document.querySelector('input').value = '';
    }
});

