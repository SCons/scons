"""Memoizer

Memoizer -- base class to provide automatic, optimized caching of
method return values for subclassed objects.  Caching is activated by
the presence of "__cacheable__" in the doc of a method (acts like a
decorator).  The presence of "__cache_reset__" or "__reset_cache__"
in the doc string instead indicates a method that should reset the
cache, discarding any currently cached values.

Note: current implementation is optimized for speed, not space.  The
cache reset operation does not actually discard older results, and in
fact, all cached results (and keys) are held indefinitely.

Most of the work for this is done by copying and modifying the class
definition itself, rather than the object instances.  This will
therefore allow all instances of a class to get caching activated
without requiring lengthy initialization or other management of the
instance.

[This could also be done using metaclassing (which would require
Python 2.2) and decorators (which would require Python 2.4).  Current
implementation is used due to Python 1.5.2 compatability requirement
contraint.]

A few notes:

    * All local methods/attributes use a prefix of "_MeMoIZeR" to avoid
      namespace collisions with the attributes of the objects
      being cached.

    * Based on performance evaluations of dictionaries, caching is
      done by providing each object with a unique key attribute and
      using the value of that attribute as an index for dictionary
      lookup.  If an object doesn't have one of these attributes,
      fallbacks are utilized (although they will be somewhat slower).

      * To support this unique-value attribute correctly, it must be
        removed whenever a __cmp__ operation is performed, and it must
        be updated whenever a copy.copy or copy.deepcopy is performed,
        so appropriate manipulation is provided by the Caching code
        below.

    * Cached values are stored in the class (indexed by the caching
      key attribute, then by the name of the method called and the
      constructed key of the arguments passed).  By storing them here
      rather than on the instance, the instance can be compared,
      copied, and pickled much easier.

Some advantages:

    * The method by which caching is implemented can be changed in a
      single location and it will apply globally.

    * Greatly simplified client code: remove lots of try...except or
      similar handling of cached lookup.  Also usually more correct in
      that it based caching on all input arguments whereas many
      hand-implemented caching operations often miss arguments that
      might affect results.

    * Caching can be globally disabled very easily (for testing, etc.)
    
"""

#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

#TBD: for pickling, should probably revert object to unclassed state...

import copy
import os
import string
import sys

#
# Generate a key for an object that is to be used as the caching key
# for that object.
#
# Current implementation: singleton generating a monotonically
# increasing integer

class MemoizerKey:
    def __init__(self):
        self._next_keyval = 0
    def __call__(self):
        r = self._next_keyval
        self._next_keyval = self._next_keyval + 1
        return str(r)
Next_Memoize_Key = MemoizerKey()


#
# Memoized Class management.
#
# Classes can be manipulated just like object instances; we are going
# to do some of that here, without the benefit of metaclassing
# introduced in Python 2.2 (it would be nice to use that, but this
# attempts to maintain backward compatibility to Python 1.5.2).
#
# The basic implementation therefore is to update the class definition
# for any objects that we want to enable caching for.  The updated
# definition performs caching activities for those methods
# appropriately marked in the original class.
#
# When an object is created, its class is switched to this updated,
# cache-enabled class definition, thereby enabling caching operations.
#
# To get an instance to used the updated, caching class, the instance
# must declare the Memoizer as a base class and make sure to call the
# Memoizer's __init__ during the instance's __init__.  The Memoizer's
# __init__ will perform the class updating.

# For Python 2.2 and later, where metaclassing is supported, it is
# sufficient to provide a "__metaclass__ = Memoized_Metaclass" as part
# of the class definition; the metaclassing will automatically invoke
# the code herein properly.

##import cPickle
##def ALT0_MeMoIZeR_gen_key(argtuple, kwdict):
##    return cPickle.dumps( (argtuple,kwdict) )

def ALT1_MeMoIZeR_gen_key(argtuple, kwdict):
    return repr(argtuple) + '|' + repr(kwdict)

def ALT2_MeMoIZeR_gen_key(argtuple, kwdict):
    return string.join(map(lambda A:
                           getattr(A, '_MeMoIZeR_Key', str(A)),
                           argtuple) + \
                       map(lambda D:
                           str(D[0])+
                           getattr(D[1], '_MeMoIZeR_Key', str(D[1])),
                           kwdict.items()),
                       '|')

def ALT3_MeMoIZeR_gen_key(argtuple, kwdict):
    ret = []
    for A in argtuple:
        X = getattr(A, '_MeMoIZeR_Key', None)
        if X:
            ret.append(X)
        else:
            ret.append(str(A))
    for K,V in kwdict.items():
        ret.append(str(K))
        X = getattr(V, '_MeMoIZeR_Key', None)
        if X:
            ret.append(X)
        else:
            ret.append(str(V))
    return string.join(ret, '|')

def ALT4_MeMoIZeR_gen_key(argtuple, kwdict):
    if kwdict:
        return string.join(map(lambda A:
                               getattr(A, '_MeMoIZeR_Key', None) or str(A),
                               argtuple) + \
                           map(lambda D:
                               str(D[0])+
                               (getattr(D[1], '_MeMoIZeR_Key', None) or str(D[1])),
                               kwdict.items()),
                           '|')
    return string.join(map(lambda A:
                        getattr(A, '_MeMoIZeR_Key', None) or str(A),
                        argtuple),
                       '!')

def ALT5_MeMoIZeR_gen_key(argtuple, kwdict):
    A = string.join(map(str, argtuple), '|')
    K = ''
    if kwdict:
        I = map(lambda K,D=kwdict: str(K)+'='+str(D[K]), kwdict.keys())
        K = string.join(I, '|')
    return string.join([A,K], '!')

def ALT6_MeMoIZeR_gen_key(argtuple, kwdict):
    A = string.join(map(str, map(id, argtuple)), '|')
    K = ''
    if kwdict:
        I = map(lambda K,D=kwdict: str(K)+'='+str(id(D[K])), kwdict.keys())
        K = string.join(I, '|')
    return string.join([A,K], '!')

def ALT7_MeMoIZeR_gen_key(argtuple, kwdict):
    A = string.join(map(repr, argtuple), '|')
    K = ''
    if kwdict:
        I = map(lambda K,D=kwdict: repr(K)+'='+repr(D[K]), kwdict.keys())
        K = string.join(I, '|')
    return string.join([A,K], '!')

def ALT8_MeMoIZeR_gen_key(argtuple, kwdict):
    ret = []
    for A in argtuple:
        X = getattr(A, '_MeMoIZeR_Key', None)
        if X:
            ret.append(X)
        else:
            ret.append(repr(A))
    for K,V in kwdict.items():
        ret.append(str(K))
        X = getattr(V, '_MeMoIZeR_Key', None)
        if X:
            ret.append(X)
        else:
            ret.append(repr(V))
    return string.join(ret, '|')

def ALT9_MeMoIZeR_gen_key(argtuple, kwdict):
    ret = []
    for A in argtuple:
        try:
            X = A.__dict__.get('_MeMoIZeR_Key', None) or repr(A)
        except (AttributeError, KeyError):
            X = repr(A)
        ret.append(X)
    for K,V in kwdict.items():
        ret.append(str(K))
        ret.append('=')
        try:
            X = V.__dict__.get('_MeMoIZeR_Key', None) or repr(V)
        except (AttributeError, KeyError):
            X = repr(V)
        ret.append(X)
    return string.join(ret, '|')

#_MeMoIZeR_gen_key = ALT9_MeMoIZeR_gen_key    # 8.8, 0.20
_MeMoIZeR_gen_key = ALT8_MeMoIZeR_gen_key    # 8.5, 0.18
#_MeMoIZeR_gen_key = ALT7_MeMoIZeR_gen_key    # 8.7, 0.17
#_MeMoIZeR_gen_key = ALT6_MeMoIZeR_gen_key    # 
#_MeMoIZeR_gen_key = ALT5_MeMoIZeR_gen_key    # 9.7, 0.20
#_MeMoIZeR_gen_key = ALT4_MeMoIZeR_gen_key    # 8.6, 0.19
#_MeMoIZeR_gen_key = ALT3_MeMoIZeR_gen_key    # 8.5, 0.20
#_MeMoIZeR_gen_key = ALT2_MeMoIZeR_gen_key    # 10.1, 0.22
#_MeMoIZeR_gen_key = ALT1_MeMoIZeR_gen_key    # 8.6 0.18



## This is really the core worker of the Memoize module.  Any
## __cacheable__ method ends up calling this function which tries to
## return a previously cached value if it exists, and which calls the
## actual function and caches the return value if it doesn't already
## exist.
##
## This function should be VERY efficient: it will get called a lot
## and its job is to be faster than what would be called.

def Memoizer_cache_get(func, cdict, args, kw):
    """Called instead of name to see if this method call's return
    value has been cached.  If it has, just return the cached
    value; if not, call the actual method and cache the return."""

    obj = args[0]

    ckey = obj._MeMoIZeR_Key + ':' + _MeMoIZeR_gen_key(args, kw)

##    try:
##        rval = cdict[ckey]
##    except KeyError:
##        rval = cdict[ckey] = apply(func, args, kw)

    rval = cdict.get(ckey, "_MeMoIZeR")
    if rval is "_MeMoIZeR":
        rval = cdict[ckey] = apply(func, args, kw)

##    rval = cdict.setdefault(ckey, apply(func, args, kw))

##    if cdict.has_key(ckey):
##        rval = cdict[ckey]
##    else:
##        rval = cdict[ckey] = apply(func, args, kw)

    return rval

def Memoizer_cache_get_self(func, cdict, self):
    """Called instead of func(self) to see if this method call's
    return value has been cached.  If it has, just return the cached
    value; if not, call the actual method and cache the return.
    Optimized version of Memoizer_cache_get for methods that take the
    object instance as the only argument."""

    ckey = self._MeMoIZeR_Key

##    try:
##        rval = cdict[ckey]
##    except KeyError:
##        rval = cdict[ckey] = func(self)

    rval = cdict.get(ckey, "_MeMoIZeR")
    if rval is "_MeMoIZeR":
        rval = cdict[ckey] = func(self)

##    rval = cdict.setdefault(ckey, func(self)))

##    if cdict.has_key(ckey):
##        rval = cdict[ckey]
##    else:
##        rval = cdict[ckey] = func(self)

    return rval

def Memoizer_cache_get_one(func, cdict, self, arg):
    """Called instead of func(self, arg) to see if this method call's
    return value has been cached.  If it has, just return the cached
    value; if not, call the actual method and cache the return.
    Optimized version of Memoizer_cache_get for methods that take the
    object instance and one other argument only."""

##    X = getattr(arg, "_MeMoIZeR_Key", None)
##    if X:
##        ckey = self._MeMoIZeR_Key +':'+ X
##    else:
##        ckey = self._MeMoIZeR_Key +':'+ str(arg)
    ckey = self._MeMoIZeR_Key + ':' + \
           (getattr(arg, "_MeMoIZeR_Key", None) or repr(arg))

##    try:
##        rval = cdict[ckey]
##    except KeyError:
##        rval = cdict[ckey] = func(self, arg)

    rval = cdict.get(ckey, "_MeMoIZeR")
    if rval is "_MeMoIZeR":
        rval = cdict[ckey] = func(self, arg)

##    rval = cdict.setdefault(ckey, func(self, arg)))

##    if cdict.has_key(ckey):
##        rval = cdict[ckey]
##    else:
##        rval = cdict[ckey] = func(self, arg)

    return rval

#
# Caching stuff is tricky, because the tradeoffs involved are often so
# non-obvious, so we're going to support an alternate set of functions
# that also count the hits and misses, to try to get a concrete idea of
# which Memoizations seem to pay off.
#
# Because different configurations can have such radically different
# performance tradeoffs, interpreting the hit/miss results will likely be
# more of an art than a science.  In other words, don't assume that just
# because you see no hits in one configuration that it's not worthwhile
# Memoizing that method.
#
# Note that these are essentially cut-and-paste copies of the above
# Memozer_cache_get*() implementations, with the addition of the
# counting logic.  If the above implementations change, the
# corresponding change should probably be made down below as well,
# just to try to keep things in sync.
#

class CounterEntry:
    def __init__(self):
        self.hit = 0
        self.miss = 0

import UserDict
class Counter(UserDict.UserDict):
    def __call__(self, obj, methname):
        k = obj.__class__.__name__ + '.' + methname
        try:
            return self[k]
        except KeyError:
            c = self[k] = CounterEntry()
            return c

CacheCount = Counter()
CacheCountSelf = Counter()
CacheCountOne = Counter()

def Dump():
    items = CacheCount.items() + CacheCountSelf.items() + CacheCountOne.items()
    items.sort()
    for k, v in items:
        print "    %7d hits %7d misses   %s()" % (v.hit, v.miss, k)

def Count_cache_get(name, func, cdict, args, kw):
    """Called instead of name to see if this method call's return
    value has been cached.  If it has, just return the cached
    value; if not, call the actual method and cache the return."""

    obj = args[0]

    ckey = obj._MeMoIZeR_Key + ':' + _MeMoIZeR_gen_key(args, kw)

    c = CacheCount(obj, name)
    rval = cdict.get(ckey, "_MeMoIZeR")
    if rval is "_MeMoIZeR":
        rval = cdict[ckey] = apply(func, args, kw)
        c.miss = c.miss + 1
    else:
        c.hit = c.hit + 1

    return rval

def Count_cache_get_self(name, func, cdict, self):
    """Called instead of func(self) to see if this method call's
    return value has been cached.  If it has, just return the cached
    value; if not, call the actual method and cache the return.
    Optimized version of Memoizer_cache_get for methods that take the
    object instance as the only argument."""

    ckey = self._MeMoIZeR_Key

    c = CacheCountSelf(self, name)
    rval = cdict.get(ckey, "_MeMoIZeR")
    if rval is "_MeMoIZeR":
        rval = cdict[ckey] = func(self)
        c.miss = c.miss + 1
    else:
        c.hit = c.hit + 1

    return rval

def Count_cache_get_one(name, func, cdict, self, arg):
    """Called instead of func(self, arg) to see if this method call's
    return value has been cached.  If it has, just return the cached
    value; if not, call the actual method and cache the return.
    Optimized version of Memoizer_cache_get for methods that take the
    object instance and one other argument only."""

    ckey = self._MeMoIZeR_Key + ':' + \
           (getattr(arg, "_MeMoIZeR_Key", None) or repr(arg))

    c = CacheCountOne(self, name)
    rval = cdict.get(ckey, "_MeMoIZeR")
    if rval is "_MeMoIZeR":
        rval = cdict[ckey] = func(self, arg)
        c.miss = c.miss + 1
    else:
        c.hit = c.hit + 1

    return rval

MCG_dict = {
    'MCG'  : Memoizer_cache_get,
    'MCGS' : Memoizer_cache_get_self,
    'MCGO' : Memoizer_cache_get_one,
}

MCG_lambda = "lambda *args, **kw: MCG(methcode, methcached, args, kw)"
MCGS_lambda = "lambda self: MCGS(methcode, methcached, self)"
MCGO_lambda = "lambda self, arg: MCGO(methcode, methcached, self, arg)"

def EnableCounting():
    """Enable counting of Memoizer hits and misses by overriding the
    globals that hold the non-counting versions of the functions and
    lambdas we call with the counting versions.
    """
    global MCG_dict
    global MCG_lambda
    global MCGS_lambda
    global MCGO_lambda

    MCG_dict = {
        'MCG'  : Count_cache_get,
        'MCGS' : Count_cache_get_self,
        'MCGO' : Count_cache_get_one,
    }

    MCG_lambda = "lambda *args, **kw: MCG(methname, methcode, methcached, args, kw)"
    MCGS_lambda = "lambda self: MCGS(methname, methcode, methcached, self)"
    MCGO_lambda = "lambda self, arg: MCGO(methname, methcode, methcached, self, arg)"



class _Memoizer_Simple:

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__dict__['_MeMoIZeR_Key'] = Next_Memoize_Key()
        #kwq: need to call original's setstate if it had one...

    def _MeMoIZeR_reset(self):
        self.__dict__['_MeMoIZeR_Key'] = Next_Memoize_Key()
        return 1


class _Memoizer_Comparable:

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__dict__['_MeMoIZeR_Key'] = Next_Memoize_Key()
        #kwq: need to call original's setstate if it had one...

    def _MeMoIZeR_reset(self):
        self.__dict__['_MeMoIZeR_Key'] = Next_Memoize_Key()
        return 1

    def __cmp__(self, other):
        """A comparison might use the object dictionaries to
        compare, so the dictionaries should contain caching
        entries.  Make new dictionaries without those entries
        to use with the underlying comparison."""

        if self is other:
            return 0

        # We are here as a cached object, but cmp will flip its
        # arguments back and forth and recurse attempting to get base
        # arguments for the comparison, so we might have already been
        # stripped.

        try:
            saved_d1 = self.__dict__
            d1 = copy.copy(saved_d1)
            del d1['_MeMoIZeR_Key']
        except KeyError:
            return self._MeMoIZeR_cmp(other)
        self.__dict__ = d1

        # Same thing for the other, but we should try to convert it
        # here in case the _MeMoIZeR_cmp compares __dict__ objects
        # directly.
        
        saved_other = None
        try:
            if other.__dict__.has_key('_MeMoIZeR_Key'):
                saved_other = other.__dict__
                d2 = copy.copy(saved_other)
                del d2['_MeMoIZeR_Key']
                other.__dict__ = d2
        except (AttributeError, KeyError):
            pass

        # Both self and other have been prepared: perform the test,
        # then restore the original dictionaries and exit
        
        rval = self._MeMoIZeR_cmp(other)

        self.__dict__ = saved_d1
        if saved_other:
            other.__dict__ = saved_other

        return rval


def Analyze_Class(klass):
    if klass.__dict__.has_key('_MeMoIZeR_converted'): return klass

    original_name = str(klass)
    
    D,R,C = _analyze_classmethods(klass.__dict__, klass.__bases__)

    if C:
        modelklass = _Memoizer_Comparable
        lcldict = {'_MeMoIZeR_cmp':C}
    else:
        modelklass = _Memoizer_Simple
        lcldict = {}

    klass.__dict__.update(memoize_classdict(klass, modelklass, lcldict, D, R))

    return klass


# Note that each eval("lambda...") has a few \n's prepended to the
# lambda, and furthermore that each of these evals has a different
# number of \n's prepended.  This is to provide a little bit of info
# for traceback or profile output, which generate things like 'File
# "<string>", line X'.  X will be the number of \n's plus 1.

# Also use the following routine to specify the "filename" portion so
# that it provides useful information.  In addition, make sure it
# contains 'os.sep + "SCons" + os.sep' for the
# SCons.Script.find_deepest_user_frame operation.

def whoami(memoizer_funcname, real_funcname):
    return '...'+os.sep+'SCons'+os.sep+'Memoizer-'+ \
           memoizer_funcname+'-lambda<'+real_funcname+'>'

def memoize_classdict(klass, modelklass, new_klassdict, cacheable, resetting):
    new_klassdict.update(modelklass.__dict__)
    new_klassdict['_MeMoIZeR_converted'] = 1

    for name,code in cacheable.items():
        eval_dict = {
            'methname' : name,
            'methcode' : code,
            'methcached' : {},
        }
        eval_dict.update(MCG_dict)
        fc = code.func_code
        if fc.co_argcount == 1 and not fc.co_flags & 0xC:
            compiled = compile("\n"*1 + MCGS_lambda,
                               whoami('cache_get_self', name),
                               "eval")
        elif fc.co_argcount == 2 and not fc.co_flags & 0xC:
            compiled = compile("\n"*2 + MCGO_lambda,
                               whoami('cache_get_one', name),
                               "eval")
        else:
            compiled = compile("\n"*3 + MCG_lambda,
                               whoami('cache_get', name),
                               "eval")
        newmethod = eval(compiled, eval_dict, {})
        new_klassdict[name] = newmethod

    for name,code in resetting.items():
        newmethod = eval(
            compile(
            "lambda obj_self, *args, **kw: (obj_self._MeMoIZeR_reset(), apply(rmethcode, (obj_self,)+args, kw))[1]",
            whoami('cache_reset', name),
            'eval'),
            {'rmethcode':code}, {})
        new_klassdict[name] = newmethod

    return new_klassdict
        

def _analyze_classmethods(klassdict, klassbases):
    """Given a class, performs a scan of methods for that class and
    all its base classes (recursively). Returns aggregated results of
    _scan_classdict calls where subclass methods are superimposed over
    base class methods of the same name (emulating instance->class
    method lookup)."""

    D = {}
    R = {}
    C = None
    
    # Get cache/reset/cmp methods from subclasses

    for K in klassbases:
        if K.__dict__.has_key('_MeMoIZeR_converted'): continue
        d,r,c = _analyze_classmethods(K.__dict__, K.__bases__)
        D.update(d)
        R.update(r)
        C = c or C

    # Delete base method info if current class has an override

    for M in D.keys():
        if M == '__cmp__': continue
        if klassdict.has_key(M):
            del D[M]
    for M in R.keys():
        if M == '__cmp__': continue
        if klassdict.has_key(M):
            del R[M]

    # Get cache/reset/cmp from current class

    d,r,c = _scan_classdict(klassdict)

    # Update accumulated cache/reset/cmp methods

    D.update(d)
    R.update(r)
    C = c or C

    return D,R,C


def _scan_classdict(klassdict):
    """Scans the method dictionary of a class to find all methods
    interesting to caching operations.  Returns a tuple of these
    interesting methods:

      ( dict-of-cachable-methods,
        dict-of-cache-resetting-methods,
        cmp_method_val or None)

    Each dict has the name of the method as a key and the corresponding
    value is the method body."""
    
    cache_setters = {}
    cache_resetters = {}
    cmp_if_exists = None
    already_cache_modified = 0

    for attr,val in klassdict.items():
        if not callable(val): continue
        if attr == '__cmp__':
            cmp_if_exists = val
            continue  # cmp can't be cached and can't reset cache
        if attr == '_MeMoIZeR_cmp':
            already_cache_modified = 1
            continue
        if not val.__doc__: continue
        if string.find(val.__doc__, '__cache_reset__') > -1:
            cache_resetters[attr] = val
            continue
        if string.find(val.__doc__, '__reset_cache__') > -1:
            cache_resetters[attr] = val
            continue
        if string.find(val.__doc__, '__cacheable__') > -1:
            cache_setters[attr] = val
            continue
    if already_cache_modified: cmp_if_exists = 'already_cache_modified'
    return cache_setters, cache_resetters, cmp_if_exists
        
#
# Primary Memoizer class.  This should be a base-class for any class
# that wants method call results to be cached.  The sub-class should
# call this parent class's __init__ method, but no other requirements
# are made on the subclass (other than appropriate decoration).

class Memoizer:
    """Object which performs caching of method calls for its 'primary'
    instance."""

    def __init__(self):
        self.__class__ = Analyze_Class(self.__class__)
        self._MeMoIZeR_Key =  Next_Memoize_Key()
    

has_metaclass = 1
# Find out if we are pre-2.2

try:
    vinfo = sys.version_info
except AttributeError:
    """Split an old-style version string into major and minor parts.  This
    is complicated by the fact that a version string can be something
    like 3.2b1."""
    import re
    version = string.split(string.split(sys.version, ' ')[0], '.')
    vinfo = (int(version[0]), int(re.match('\d+', version[1]).group()))
    del re

need_version = (2, 2) # actual
#need_version = (33, 0)  # always
#need_version = (0, 0)  # never
if vinfo[0] < need_version[0] or \
   (vinfo[0] == need_version[0] and
    vinfo[1] < need_version[1]):
    has_metaclass = 0
    class Memoized_Metaclass:
        # Just a place-holder so pre-metaclass Python versions don't
        # have to have special code for the Memoized classes.
        pass
else:

    # Initialization is a wee bit of a hassle.  We want to do some of
    # our own work for initialization, then pass on to the actual
    # initialization function.  However, we have to be careful we
    # don't interfere with (a) the super()'s initialization call of
    # it's superclass's __init__, and (b) classes we are Memoizing
    # that don't have their own __init__ but which have a super that
    # has an __init__.  To do (a), we eval a lambda below where the
    # actual init code is locally bound and the __init__ entry in the
    # class's dictionary is replaced with the _MeMoIZeR_init call.  To
    # do (b), we use _MeMoIZeR_superinit as a fallback if the class
    # doesn't have it's own __init__.  Note that we don't use getattr
    # to obtain the __init__ because we don't want to re-instrument
    # parent-class __init__ operations (and we want to avoid the
    # Object object's slot init if the class has no __init__).
    
    def _MeMoIZeR_init(actual_init, self, args, kw):
        self.__dict__['_MeMoIZeR_Key'] =  Next_Memoize_Key()
        apply(actual_init, (self,)+args, kw)

    def _MeMoIZeR_superinit(self, cls, args, kw):
        apply(super(cls, self).__init__, args, kw)
        
    class Memoized_Metaclass(type):
        def __init__(cls, name, bases, cls_dict):
            # Note that cls_dict apparently contains a *copy* of the
            # attribute dictionary of the class; modifying cls_dict
            # has no effect on the actual class itself.
            D,R,C = _analyze_classmethods(cls_dict, bases)
            if C:
                modelklass = _Memoizer_Comparable
                cls_dict['_MeMoIZeR_cmp'] = C
            else:
                modelklass = _Memoizer_Simple
            klassdict = memoize_classdict(cls, modelklass, cls_dict, D, R)

            init = klassdict.get('__init__', None)
            if not init:
                # Make sure filename has os.sep+'SCons'+os.sep so that
                # SCons.Script.find_deepest_user_frame doesn't stop here
                import inspect # It's OK, can't get here for Python < 2.1
                superinitcode = compile(
                    "lambda self, *args, **kw: MPI(self, cls, args, kw)",
                    inspect.getsourcefile(_MeMoIZeR_superinit) or '<unknown>',
                    "eval")
                superinit = eval(superinitcode,
                                 {'cls':cls,
                                  'MPI':_MeMoIZeR_superinit})
                init = superinit
                
            newinitcode = compile(
                "\n"*(init.func_code.co_firstlineno-1) +
                "lambda self, args, kw: _MeMoIZeR_init(real_init, self, args, kw)",
                whoami('init', init.func_code.co_filename),
                'eval')
            newinit = eval(newinitcode,
                           {'real_init':init,
                            '_MeMoIZeR_init':_MeMoIZeR_init},
                           {})
            klassdict['__init__'] = lambda self, *args, **kw: newinit(self, args, kw)

            super(Memoized_Metaclass, cls).__init__(name, bases, klassdict)
            # Now, since klassdict doesn't seem to have affected the class
            # definition itself, apply klassdict.
            for attr in klassdict.keys():
                setattr(cls, attr, klassdict[attr])
                
