// Connect to NumWorks calculator and print platformInfo
const Numworks = require('upsilon.js')
const usb = require('usb');

const DEBUG = false;

// Init webusb
navigator = {}
navigator.usb = usb.webusb

// Add navigator to Numworks
Numworks.navigator = navigator

// Create calculator object
var calculator = new Numworks()

navigator.usb.addEventListener('disconnect', function (e) {
    calculator.onUnexpectedDisconnect(e, function () {
        log("Disconnected from calculator")
    })
})

// Disable WebDFU logging to avoid spamming the console
function disableWebDFULogging(calculator) {
    calculator.device.logDebug = function () { }
    calculator.device.logInfo = function () { }
    calculator.device.logWarning = function () { }
    calculator.device.logError = function () { }
    calculator.device.logProgress = function () { }
}

// Called when calculator is connected
function onConnect() {
    disableWebDFULogging(calculator)
}

function log(msg) {
    if (!DEBUG) {
        return
    }
    // Write to stderr, so other script can read from stdout
    console.error(msg)

    // Also write to a file named log.txt
    const fs = require('fs');
    fs.appendFile('log.txt', msg + "\n", function (err) {
        if (err) throw err;
    });
}

// Connect to calculator
async function connect() {
    log("Connecting to calculator...")

    // While calculator is not connected, try to connect
    while (calculator.device == null) {
        await calculator.detect(onConnect, function () { })
    }
    log("Connected to calculator")
    return {status: "connected"}
}

async function disconnect() {
    log("Disconnecting from calculator...")
    if (calculator.device != null) {
        calculator.device.close()
    }
    // Create a new calculator object to avoid any error
    calculator = new Numworks()
    log("Disconnected from calculator")
    return {status: "disconnected"}
}

async function status() {
    if (calculator.device == null) {
        return {status: "disconnected"}
    } else {
        return {status: "connected"}
    }
}

async function installStorage(storage) {
    // Install storage (we need to instantiate a new storage object because
    // Python script can't access the storage object)
    log("Installing storage...")

    // Instantiate a new storage object
    const storage_instance = new Numworks.Storage()
    storage_instance.records = []

    // Add all the records into the storage object
    for (const record of storage.records) {
        // Convert record.data to a Blob object
        record.data = new Blob([record.data])
        storage_instance.records.push(record)
    }

    await calculator.installStorage(storage_instance, function () { })
    log("Storage installed")

    return {status: "ok"}
}

// JSON interactive shell that is used from another script.
async function interactivity() {
    log("Starting interactivity")
    process.stdin.setEncoding('utf8');
    let buffer = ""
    process.stdin.on('readable', async () => {
        let chunk;
        while ((chunk = process.stdin.read()) !== null) {
            try {
                // If \n is not found, add chunk to buffer and continue
                if (chunk[chunk.length - 1] != "\n") {
                    buffer += chunk
                    continue
                } else if (buffer != "") {
                    // If \n is found, add chunk to buffer and set chunk to buffer
                    buffer += chunk
                    chunk = buffer
                    buffer = ""
                }
                const data = JSON.parse(chunk)

                // If method is connect, connect to calculator
                if (data.method == "connect") {
                    const result = await connect()
                    // const result = "{connected: true}"
                    process.stdout.write(JSON.stringify(result) + "\n")
                    continue
                } else if (data.method == "disconnect") {
                    const result = await disconnect()
                    process.stdout.write(JSON.stringify(result) + "\n")
                    continue
                } else if (data.method == "status") {
                    const result = await status()
                    process.stdout.write(JSON.stringify(result) + "\n")
                    continue
                } else if (data.method == "installStorage") {
                    const result = await installStorage(...data.args)
                    process.stdout.write(JSON.stringify(result) + "\n")
                    continue
                } else if (data.method == "exit") {
                    log("Exiting")
                    process.exit(0)
                }

                // If data.args is undefined, set it to an empty array
                if (data.args == undefined) {
                    data.args = []
                }

                log("Running " + data.method + "(" + data.args + ")")

                // Run calculator.(data.method)(data.args)
                const result = await calculator[data.method](...data.args)

                // Write result to stdout
                process.stdout.write(JSON.stringify(result) + "\n")
            } catch (e) {
                log(e)
                log("Error while handling: " + chunk)
                e = e.toString()
                process.stdout.write(JSON.stringify({error: e}) + "\n")
            }
        }
    });

    process.stdin.on('end', () => {
        process.stdout.write(JSON.stringify({error: "stdin closed"}) + "\n")
        log("Exiting")
        process.exit(0)
    });

    // Inform that the script is ready to receive data
    process.stdout.write(JSON.stringify({ready: true}) + "\n")
}

async function main() {
    // In debug mode, clear log file
    if (DEBUG) {
        const fs = require('fs');
        fs.writeFile('log.txt', '', function (err) {
            if (err) throw err;
        });
    }
    await interactivity()
}

main()
