# Usage

## Setting variables
  * Variables can be set to contain
    1. Plain strings
    1. Strings with multiple tokens (white space separated)
    1. Lists of strings
    1. Strings to be evaluated by Python (Surrounded by ${ })
    1. Strings with variable references in them (prefixed by $ or wrapped with ${})
    
# Subst usage
  * Called one of two ways
    * subst() meant to return a string (a single command line or other)
    * subst_list() meant to return an array of arrays (an array of array of command line arguments suitable for os.system or similar)
  * All usage must refer to variables values via $ or ${}
    * "$(" "$)" are used to escape parts of the line which shouldn't be used for a signature  

# Objects:
  * EnvironmentValue
    * This will hold a single value, and all if it's non context dependent information
      * The value broken into tokens
      * The type of the value
      * A method to expand the value into a string?
      * What should this do?
        * Store value
        * Store tokenized version of value
          * The types of some tokens may depend on the context? Do we actually store this info in EnvironmentValues?
        * Store info on what this value depends on (which other values)
        * ? store cached value?
        * Store value type? (It may not be possible to know this without knowing the contents/types of other values?)
  * EnvironmentValues
    * Hold a dictionary of all variables and their EnvironmentValue objects
    * Has staticmethod to evaluate a string ( *subst()* )
    * Has staticmethod to evaluate a list ( *subst_list()* )
    * Holds all caches, and each symbols direct dependencies. (To enable invalidating cached values)
    * Holds a collection of EnvironmentValue objects, addressable by the string they contain. In some cases this is the variable itself, in other cases this is a string or list of elements passed to *subst()* or *subst_list()* which is being stored to be able to be cached.
    
# String Tokenizing
## Given a string what tokens can we definitively identify without context
  * Plain string (No $)
  * White space
  * Escape open $( and Escape close $)
  * Special variable (SOURCES, TARGETS, SOURCE, TARGET, CHANGED_SOURCES, 
                      CHANGED_TARGETS, UNCHANGED_SOURCES, UNCHANGED_TARGETS)
  * Variable or Callable ( Prefixed by $ must begin with alphabetic or underscore)
  * Evaluable only (Contains a . or a [ inside ${ })
  * Function call  ${SOMEFUNCTION(ARG1,ARG2)}
  * Quote?
  
## What types of tokens are only identifiable given context (values of other variables)
  * Callable
  * Variable when the token could have been either Variable or Callable
  
  

# Caching
  * Where do we cache it?
    * In the EnvironmentValues - (since this will have the context)
  * What can we cache?
    * Simple string replacement:
      * $A='B'
        * A.cached='B'
      * $A='$B', $B='ZZ'
        * A.cached='ZZ'
        * A.depends_on = ['B']
        * B.cached='ZZ'
      * $A='$B $C $D', $B='BB', $C='CC', $D='DD'
        * D.cached='DD'
        * C.cached='CC'
        * B.cached='BB'
        * A.cached='BB CC DD'
        * A.depends_on=['B','C','D'] <- or references to B, C, D?
    * Functions which tell us they can be cached and what effects them
      * def A(x): return 'ZZ'
      * A.affected_by=[] # not affected by any other variables
      * $Z='${A("BB")}'
      * A.cached='ZZ'
      * Z.cached='ZZ'
      * Z.depends_on=['A']

  * What can't we cache?
    * Functions which don't tell us they can be cached
      * def A(x): return 'ZZ'
      * $Z='${A("BB")}'
    * Strings which will be evaluated
      * $AA='${B.absdir}'
      * $BB="${if A=='zz' then 'XXX'}"
  * We never cache evaluated special variables (See above.. TARGET..etc). But we can cache the rest of such command lines subject to limitations below.
  * All caching is lists of tokens (both string and as yet unconverted). Flattened?


# subst() Functionality
  * Each evaluation can yield one or more (in a list or dictionary) of the following
    * Simple string -> 'A'
    * Escape Marker -> '$(' or '$)' if not for signature and not for command line (in raw mode)
    * White space -> ' '
    * Variable -> '$A'
    * Evaluable string -> "xyz" or "xyz('a','b')" or "if A=True: print("Yup") else: print("Nope")'
    * Callable -> 
  * If a single token's evaluation yields more than one value then we insert into the string and variable list we're processing that number of elements and put each element of the return value in the appropriate list
    * or do we add a token type which indicates another level of evaluation hierarchy? (Downside we need to keep this context when processing. This is likely not a good approach)
  
# subst_list() Functionality  
  * It's expected to return an array of return values. Each array is effectively a single command line and should also contain a list of the results
    * When there's effectively only a single line, then only return_value[0] has anything in it.
    * When there's a newline in the list being evaluated, that instructions subst_list to create a new list and add to the return value array
      * return_value[1]=[].. then append the results of successive evaluations there to the end (unless it hits another end of line character)
  * Each item in the list item being worked on is evaluated similar to subst()?
  
# Subst Algorithm
  * Check if plain string and no '$', then just return the string. (optimization)
  * Get global variable dictionary
    * These are all EnvironmentValue objects
  * Get (or create) local variable dictionary
    * Only overrides are EnvironmentValue objects
    * **NOTE**: This is what  OverRideEnvironments use to pass their overrides in addition to the TARGET/SOURCE which is normally in local variable dictionary
  * Convert referenced Special variables to EnvironmentValue objects when needed. (They will be generated via factory and cached)
  * Is it (probably) worth creating some shortcut logic where if the value we're trying to subst is only one token and that token is a plain string, we just return it. Though we may have to take into account that it's a simple string with multiple tokens "a simple string" rather than something like ".obj"
  * Create an EnvironmentValue from the string to be substituted.
  * Walk each token and evaluate
    * Plain string. Do nothing
    * $VALUE - env.Subst
    * ${VALUE} - env.Subst
    * ${VALUE.method} - Evaluable
    * Whitespace?
    * Escape?
    * Check if the variable is one of the reserved construction variables. (We need to be sure we don't cache these)
    
    
#def scons_subst_once(strSubst, env, key):
  * Need to re-implement this such that it works with the new Subst implementation.
  * Basically if we're working on key X and the call has X='$X other stuff', X should end up with the contents of X and the other stuff. Give X="fun stuff $OTHER", X="fun stuff $OTHER other stuff" after the call with the above.
  
# EnvironmentValue
  * These objects need to be unique (for any given string value, there is only one EnvironmentValue object)
    