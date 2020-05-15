
# EZEE AI

## Description
A GUI-based platform for deep learning. This tool is based on tensorflow and tensorflow.js. 

## Installation

#### Python

We assume that Python 3 is the default python interpreter. By running from the terminal the following command, all the required packages will be installed:
```bash
pip install -r requirements.txt
```

In a terminal, execute the following command (Python 3 is the assumed python interpreter):
```python
python wsgi.py
```

#### Docker
```bash
docker run -p 5000:5000 -p 55500:55600 machine2learn/ezeeai
```

You can use the application by launching chrome browser and connecting to http://localhost:5000. 

To save your model after docker finishes you can mount a volume to `/tmp/data` like so:
```bash
docker run -p 5000:5000 -p 55500-55600:55500-55600 -v $(pwd)/data:/tmp/data machine2learn/ezeeai
```


To login you can use the following credentials:

| Username | Password |
| -------- | ---- |
| test | test_machine2learn |
