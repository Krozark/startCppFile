#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse

def get_tab(depth):
    tab = ""
    for u in xrange(0,depth):
        tab+="    "
    return tab

def line(depth,txt):
    return "%s%s\n" % (get_tab(depth),txt)

class Function(object):
    def __init__(self,ret="",name="",params="",template="",klass=None,delete=False):
        self.ret = ret
        self.name = name
        self.params = params
        self.template = template
        self.klass=klass
        self.delete=delete

    def __to_proto(self,klass=None,depth=0):
        l=""
        if klass:
            l+=line(depth,klass.template)

        if self.template:
            l+=line(depth,self.template)

        l2=""
        if self.ret:
            l2+= self.ret+" "

        if klass:
            l2+=klass.name+"::"

        l2+=self.name+"("
        if self.params:
            l2+=self.params[0]
            for u in self.params[1:]:
                l2+=","+u
        l2+=')'

        l+=get_tab(depth)+l2
        return l

    def to_hpp(self,depth=0):
        l=self.__to_proto(depth=depth)
        if self.delete:
            l+=" = delete"
        l+=";\n"
        return l

    def to_cpp(self,depth=0):
        r=""
        if self.delete:
            return r
        r = self.__to_proto(klass=self.klass,depth=depth)+"\n"
        r+=line(depth,"{")
        if self.ret:
            r+=line(depth+1,"return;")
        r+=line(depth,"}")
        return r

class Class(object):
    def __init__(self,name="",template=""):
        self.name = name
        self.template = template
        self.depth = 0
        self.functions = []

    def _as_const_ref(self):
        return "const %s&" % self.name

    def _as_ref(self):
        return "%s&" % self.name

    def add_function(self,function):
        self.functions.append(function)

    def add_constructor(self,delete=False):
        self.add_function(Function(name=self.name,
                                   klass=self,
                                   delete=delete))

    def add_copy_constructor(self,delete=False):
        self.add_function(Function(name=self.name,
                                   params=[self._as_const_ref()],
                                   klass=self,
                                   delete=delete))

    def add_assignement(self,delete=False,params=None):
        if not params:
            params = [self._as_const_ref(),]
        self.add_function(Function(ret=self._as_ref(),
                                   params=params,
                                   klass=self,
                                   delete = delete))


    def to_hpp(self):
        r = line(self.depth,"class %s" % self.name)
        r+= line(self.depth,"{")
        for f in self.functions:
            r+= f.to_hpp(self.depth+1)
        r+= line(self.depth,"};")
        return r

    def to_cpp(self):
        r = ""
        for f in self.functions:
            r+= f.to_cpp(self.depth)
        return r


class Render(object):
    def __init__(self,namespaces,classname):
        self.hpp_filename = "%s.hpp" % classname
        self.cpp_filename = "%s.cpp" % classname
        self.classname  = classname
        self.namespaces = namespaces
        self.klass = []

    def add_class(self,klass):
        klass.depth = len(self.namespaces)
        self.klass.append(klass)

    def to_hpp(self):
        try:
            f = open(self.hpp_filename,"r")
            print "file %s already exist" % self.hpp_filename
            f.close()
        except:
            pass
        f = file(self.hpp_filename,"w+")
        guard = "_".join([x.upper() for x in self.namespaces+[self.classname,"hpp"]])

        #start guard
        f.write("#ifndef %s\n" % guard)
        f.write("#define %s\n\n" % guard)

        for depth,name in enumerate(self.namespaces):
            f.write(line(depth,"namespace %s" % name))
            f.write(line(depth,"{"))

        for klass in self.klass:
            f.write(klass.to_hpp())

        r = range(0,len(self.namespaces))
        r.reverse()
        for depth in r:
            f.write(line(depth,"}"))

        f.write("#endif")
        f.close()

    def to_cpp(self):
        try:
            f = open(self.cpp_filename,"r")
            print "file %s already exist" % self.cpp_filename
            f.close()
        except:
            pass
        f = file(self.cpp_filename,"w+")

        #include
        f.write("#include <%s>\n\n" % self.hpp_filename)

        for depth,name in enumerate(self.namespaces):
            f.write(line(depth,"namespace %s" % name))
            f.write(line(depth,"{"))

        for klass in self.klass:
            f.write(klass.to_cpp())

        r = range(0,len(self.namespaces))
        r.reverse()
        for depth in r:
            f.write(line(depth,"}"))
        f.close()


def main(argv):
    #args
    parser = argparse.ArgumentParser()
    parser.add_argument("classname", help="the name of the class to create",type=str)
    parser.add_argument("--no-copy", help="make a none copyable class",action="store_true")
    parser.add_argument('-n', '--namespace', nargs='+', type=str,default=[])
    parser.add_argument("--hpp", help="build hpp file",action="store_true",default=False)
    parser.add_argument("--cpp", help="build cpp file",action="store_true",default=False)

    args = parser.parse_args()
    args.classname = args.classname.title()
    args.namespace = [x.lower() for x in args.namespace]

    #build klass
    klass = Class(args.classname)
    klass.add_constructor();

    if args.no_copy:
        klass.add_copy_constructor(delete=True)
        klass.add_assignement(delete=True)

    #build renderer
    r = Render(args.namespace,args.classname)
    r.add_class(klass)

    if args.hpp or not (args.hpp or args.cpp):
        r.to_hpp()

    if args.cpp or not (args.hpp or args.cpp):
        r.to_cpp()
    

if __name__ == "__main__":
   main(sys.argv[1:])
