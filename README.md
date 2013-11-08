startCppFile
============

A simple script to auto make initial cpp and/or hpp file.
Specify your classname, namespace and others options:

    usage: start_cpp_file.py [-h] [--no-copy] [-n NAMESPACE [NAMESPACE ...]]
                             [--hpp] [--cpp]
                             classname

    positional arguments:
      classname             the name of the class to create

    optional arguments:
      -h, --help            show this help message and exit
      --no-copy             make a none copyable class
      -n NAMESPACE [NAMESPACE ...], --namespace NAMESPACE [NAMESPACE ...]
      --hpp                 build hpp file
      --cpp                 build cpp file

if no --cpp and --hpp are specify, both are build.


