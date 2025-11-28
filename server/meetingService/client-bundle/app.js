// Connect to LOCAL server - NO INTERNET
const SERVER_IP = '192.168.100.183'; // ⚠️ Your server's LAN IP
const SERVER_PORT = 3000;

const client = new SFUClient(`https://${SERVER_IP}:${SERVER_PORT}`);

// Rest of the code same as before...