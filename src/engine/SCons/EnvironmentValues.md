#Objects:
  * EnvironmentValue
    * This will hold a single value, and all if it's information
      * all tokens
      * the type of the value
      * cached evaluation.  - Perhaps this should be move up to EnvironmentValues as the value really depends on the context and the context comes from EnvironmentValues
      * method to expand the value into a string?
      * What should this do?
        * Store value
        * Store tokenized version of value
          * The types of some tokens may depend on the context? Do we actually store this info in EnvironmentValues?
        * Store info on what this value depends on (which other values)
        * ? store cached value?
        * Store value type? (It may not be possible to know this without knowing the contents/types of other values?)
  * EnvironmentValues
    * Hold a dictionary of all variables and their EnvironmentValue objects
    * Has staticmethod to evaluate a string
    * Has staticmethod to evaluate a list
    
#Caching
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
      * return_value[1]=[].. then append the results of succesive evaluations there to the end (unless it hits another end of line character)
  * Each item in the list item being worked on is evaluated similar to subst()?