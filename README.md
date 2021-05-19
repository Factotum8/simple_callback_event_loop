# Simple callback event loop

## The project description

It is my implementation of event loop based on callback. 

- `./main.py` - The simple client sends one message. 
- `./demo_server.py` - The echo server receives and sends back. 

## References
    
* [overview article](https://webdevblog.ru/obzor-async-io-v-python-3-7/)
* [guid](https://iximiuz.com/en/posts/explain-event-loop-in-100-lines-of-code/)

## Requirements

 **Python >= 3.9** and libraries:
- [loguru](https://github.com/Delgan/loguru)

## Install 

* Production requirements: `python setup.py install`.
* Test requirements: `pip install -e .[test]` (if necessary).  

## Run 
In terminal:
`python ./demo_server.py 8080`  
In other terminal:
`python ./main.py 8080`

## Sources

1. python source files:
    * `./event_loop/_globals.py` - classes, function, variables which are used by other project modules.
    * `./event_loop/_socket.py` - socket which is ready for async I/O.
    * `./event_loop/event_loop.py` - class registers and unregisters _sockets. 
    * `./event_loop/queue.py` - class contains registered _sockets. 

## License
[LICENSE MIT](LICENSE)
