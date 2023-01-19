# Upsilon.py

Upsilon.py is a wrapper for [upsilon.js]. It allow controlling the NumWorks from
Python. To use this library, because of the dependency on Upsilon.js, you will
need a working installation of [Node] with [Npm]

## Installation

To install Upsilon.py, you can use pip:

```bash
python3 -m pip install upsilon.py
```

After the installation, you will have to install Upsilon.js and its
dependencies:

```bash
npm install -g "upsilon.js@^1.4.1" usb
```

## Usage

To use Upsilon.py, you will need to import it:

```python
import upsilon_py
```

Then, you can create a new NumWorks object:

```python
numworks = upsilon_py.NumWorks()
```

You will then be able to start the object and connect to the NumWorks:

```python
await numworks.start()
await numworks.connect()
```

Now, the connection is established, you can send commands to the NumWorks:

```python
# Get the status of the NumWorks (connected/disconnected)
status = await numworks.status()
print("Status:", status)

# Get the model of the NumWorks (return 100/110/120)
model = await numworks.get_model()
print("Model:", model)

# Get the platform info of the NumWorks (information about the OS)
platform_info = await numworks.get_platform_info()
print("Platform info:", platform_info)

# Backup the storage of the NumWorks
storage = await numworks.backup_storage()

# Add a file to the storage
storage["records"].append({
    "name": "Test",
    "type": "py",
    "autoImport": True,
    "code": "print(\"Hello World!\")"
})

# Install the modified storage
await numworks.install_storage(storage)

# Stop the object (you can also use numworks.disconnect() to keep the object
# running and connect to another NumWorks)
await numworks.stop()
```



[upsilon.js]: https://www.npmjs.com/package/upsilon.js
[Node]: https://nodejs.org/en/
[Npm]: https://www.npmjs.com/
