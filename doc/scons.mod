<!--

  __COPYRIGHT__

  An SCons-specific DTD module, for use with SCons DocBook
  documentation, that contains names, phrases, acronyms, etc. used
  throughout the SCons documentation.

-->

<!--

  Us, and our command names

  Convention: use &SCons; to refer to the project as a concept,
  use &scons; to refer to a command as you would invoke it.

-->

<!ENTITY SCons          "<application xmlns='http://www.scons.org/dbxsd/v1.0'>SCons</application>">
<!ENTITY scons          "<command xmlns='http://www.scons.org/dbxsd/v1.0'>scons</command>">
<!ENTITY scons-time     "<command xmlns='http://www.scons.org/dbxsd/v1.0'>scons-file</command>">
<!ENTITY sconsign       "<command xmlns='http://www.scons.org/dbxsd/v1.0'>sconsign</command>">



<!--

  Other applications that we reference.

-->

<!ENTITY Aegis          "<application xmlns='http://www.scons.org/dbxsd/v1.0'>Aegis</application>">
<!ENTITY Ant            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>Ant</application>">
<!ENTITY ar             "<application xmlns='http://www.scons.org/dbxsd/v1.0'>ar</application>">
<!ENTITY as             "<application xmlns='http://www.scons.org/dbxsd/v1.0'>as</application>">
<!ENTITY Autoconf       "<application xmlns='http://www.scons.org/dbxsd/v1.0'>Autoconf</application>">
<!ENTITY Automake       "<application xmlns='http://www.scons.org/dbxsd/v1.0'>Automake</application>">
<!ENTITY bison          "<application xmlns='http://www.scons.org/dbxsd/v1.0'>bison</application>">
<!ENTITY cc             "<application xmlns='http://www.scons.org/dbxsd/v1.0'>cc</application>">
<!ENTITY Cons           "<application xmlns='http://www.scons.org/dbxsd/v1.0'>Cons</application>">
<!ENTITY cp             "<application xmlns='http://www.scons.org/dbxsd/v1.0'>cp</application>">
<!ENTITY csh            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>csh</application>">
<!ENTITY f77            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>f77</application>">
<!ENTITY f90            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>f90</application>">
<!ENTITY f95            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>f95</application>">
<!ENTITY gas            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>gas</application>">
<!ENTITY gcc            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>gcc</application>">
<!ENTITY g77            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>g77</application>">
<!ENTITY gXX            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>gXX</application>">
<!ENTITY Jam            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>Jam</application>">
<!ENTITY jar            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>jar</application>">
<!ENTITY javac          "<application xmlns='http://www.scons.org/dbxsd/v1.0'>javac</application>">
<!ENTITY javah          "<application xmlns='http://www.scons.org/dbxsd/v1.0'>javah</application>">
<!ENTITY latex          "<application xmlns='http://www.scons.org/dbxsd/v1.0'>latex</application>">
<!ENTITY lex            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>lex</application>">
<!ENTITY m4             "<application xmlns='http://www.scons.org/dbxsd/v1.0'>m4</application>">
<!ENTITY Make           "<application xmlns='http://www.scons.org/dbxsd/v1.0'>Make</application>">
<!ENTITY Makepp         "<application xmlns='http://www.scons.org/dbxsd/v1.0'>Make++</application>">
<!ENTITY pdflatex       "<application xmlns='http://www.scons.org/dbxsd/v1.0'>pdflatex</application>">
<!ENTITY pdftex         "<application xmlns='http://www.scons.org/dbxsd/v1.0'>pdftex</application>">
<!ENTITY Python         "<application xmlns='http://www.scons.org/dbxsd/v1.0'>Python</application>">
<!ENTITY ranlib         "<application xmlns='http://www.scons.org/dbxsd/v1.0'>ranlib</application>">
<!ENTITY rmic           "<application xmlns='http://www.scons.org/dbxsd/v1.0'>rmic</application>">
<!ENTITY ScCons         "<application xmlns='http://www.scons.org/dbxsd/v1.0'>ScCons</application>">
<!ENTITY sleep          "<application xmlns='http://www.scons.org/dbxsd/v1.0'>sleep</application>">
<!ENTITY swig           "<application xmlns='http://www.scons.org/dbxsd/v1.0'>swig</application>">
<!ENTITY tar            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>tar</application>">
<!ENTITY tex            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>tex</application>">
<!ENTITY touch          "<application xmlns='http://www.scons.org/dbxsd/v1.0'>touch</application>">
<!ENTITY yacc           "<application xmlns='http://www.scons.org/dbxsd/v1.0'>yacc</application>">
<!ENTITY zip            "<application xmlns='http://www.scons.org/dbxsd/v1.0'>zip</application>">


<!--

  Classes.

-->

<!ENTITY Action "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Action</classname>">
<!ENTITY ActionBase "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>ActionBase</classname>">
<!ENTITY BuildInfo "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>BuildInfo</classname>">
<!ENTITY CommandAction "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>CommandAction</classname>">
<!ENTITY FunctionAction "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>FunctionAction</classname>">
<!ENTITY ListAction "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>ListAction</classname>">
<!ENTITY Builder "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Builder</classname>">
<!ENTITY BuilderBase "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>BuilderBase</classname>">
<!ENTITY CompositeBuilder "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>CompositeBuilder</classname>">
<!ENTITY MultiStepBuilder "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>MultiStepBuilder</classname>">
<!ENTITY Job "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Job</classname>">
<!ENTITY Jobs "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Jobs</classname>">
<!ENTITY Serial "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Serial</classname>">
<!ENTITY Parallel "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Parallel</classname>">
<!ENTITY Node "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Node</classname>">
<!ENTITY Node_FS "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Node.FS</classname>">
<!ENTITY Scanner "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Scanner</classname>">
<!ENTITY Sig "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Sig</classname>">
<!ENTITY Signature "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Signature</classname>">
<!ENTITY Taskmaster "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Taskmaster</classname>">
<!ENTITY TimeStamp "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>TimeStamp</classname>">
<!ENTITY Walker "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Walker</classname>">
<!ENTITY Wrapper "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>Wrapper</classname>">



<!--

  Options, command-line.

-->

<!ENTITY config "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--config</option>">
<!ENTITY debug-duplicate "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--debug=duplicate</option>">
<!ENTITY debug-explain "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--debug=explain</option>">
<!ENTITY debug-findlibs "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--debug=findlibs</option>">
<!ENTITY debug-includes "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--debug=includes</option>">
<!ENTITY debug-prepare "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--debug=prepare</option>">
<!ENTITY debug-presub "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--debug=presub</option>">
<!ENTITY debug-stacktrace "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--debug=stacktrace</option>">
<!ENTITY implicit-cache "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--implicit-cache</option>">
<!ENTITY implicit-deps-changed "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--implicit-deps-changed</option>">
<!ENTITY implicit-deps-unchanged "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--implicit-deps-unchanged</option>">
<!ENTITY profile "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--profile</option>">
<!ENTITY taskmastertrace "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--taskmastertrace</option>">
<!ENTITY tree "<option xmlns='http://www.scons.org/dbxsd/v1.0'>--tree</option>">
<!ENTITY Q "<option xmlns='http://www.scons.org/dbxsd/v1.0'>-Q</option>">

<!--

  Options, SConscript-settable.

-->

<!ENTITY implicit_cache "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>implicit_cache</literal>">
<!ENTITY implicit_deps_changed "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>implicit_deps_changed</literal>">
<!ENTITY implicit_deps_unchanged "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>implicit_deps_unchanged</literal>">



<!--

  File and directory names.

-->

<!ENTITY build "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>build</filename>">
<!ENTITY Makefile "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>Makefile</filename>">
<!ENTITY Makefiles "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>Makefiles</filename>">
<!ENTITY SConscript "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>SConscript</filename>">
<!ENTITY SConstruct "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>SConstruct</filename>">
<!ENTITY Sconstruct "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>Sconstruct</filename>">
<!ENTITY sconstruct "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>sconstruct</filename>">
<!ENTITY SConstruct.py "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>SConstruct.py</filename>">
<!ENTITY Sconstruct.py "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>Sconstruct.py</filename>">
<!ENTITY sconstruct.py "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>sconstruct.py</filename>">
<!ENTITY sconsigndb "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>.sconsign</filename>">
<!ENTITY src "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>src</filename>">



<!--

  Methods and functions.  This includes functions from both
  the Build Engine and the Native Python Interface.

-->

<!ENTITY Add "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Add</function>">
<!ENTITY AddMethod "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AddMethod</function>">
<!ENTITY AddPostAction "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AddPostAction</function>">
<!ENTITY AddPreAction "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AddPreAction</function>">
<!ENTITY AddOption "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AddOption</function>">
<!ENTITY AddOptions "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AddOptions</function>">
<!ENTITY AddVariables "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AddVariables</function>">
<!ENTITY Alias "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Alias</function>">
<!ENTITY Aliases "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Aliases</function>">
<!ENTITY AllowSubstExceptions "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AllowSubstExceptions</function>">
<!ENTITY AlwaysBuild "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AlwaysBuild</function>">
<!ENTITY Append "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Append</function>">
<!ENTITY AppendENVPath "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AppendENVPath</function>">
<!ENTITY AppendUnique "<function xmlns='http://www.scons.org/dbxsd/v1.0'>AppendUnique</function>">
<!ENTITY BoolOption "<function xmlns='http://www.scons.org/dbxsd/v1.0'>BoolOption</function>">
<!ENTITY BoolVariable "<function xmlns='http://www.scons.org/dbxsd/v1.0'>BoolVariable</function>">
<!ENTITY Build "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Build</function>">
<!ENTITY CacheDir "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CacheDir</function>">
<!ENTITY Chmod "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Chmod</function>">
<!ENTITY Clean "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Clean</function>">
<!ENTITY Clone "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Clone</function>">
<!ENTITY Command "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Command</function>">
<!ENTITY Configure "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Configure</function>">
<!ENTITY Copy "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Copy</function>">
<!ENTITY Decider "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Decider</function>">
<!ENTITY Default "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Default</function>">
<!ENTITY DefaultEnvironment "<function xmlns='http://www.scons.org/dbxsd/v1.0'>DefaultEnvironment</function>">
<!ENTITY DefaultRules "<function xmlns='http://www.scons.org/dbxsd/v1.0'>DefaultRules</function>">
<!ENTITY Delete "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Delete</function>">
<!ENTITY Depends "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Depends</function>">
<!ENTITY Dir "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Dir</function>">
<!ENTITY Dump "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Dump</function>">
<!ENTITY Duplicate "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Duplicate</function>">
<!ENTITY Entry "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Entry</function>">
<!ENTITY EnumOption "<function xmlns='http://www.scons.org/dbxsd/v1.0'>EnumOption</function>">
<!ENTITY EnumVariable "<function xmlns='http://www.scons.org/dbxsd/v1.0'>EnumVariable</function>">
<!ENTITY EnsurePythonVersion "<function xmlns='http://www.scons.org/dbxsd/v1.0'>EnsurePythonVersion</function>">
<!ENTITY EnsureSConsVersion "<function xmlns='http://www.scons.org/dbxsd/v1.0'>EnsureSConsVersion</function>">
<!ENTITY Environment "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Environment</function>">
<!ENTITY Execute "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Execute</function>">
<!ENTITY Exit "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Exit</function>">
<!ENTITY Export "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Export</function>">
<!ENTITY File "<function xmlns='http://www.scons.org/dbxsd/v1.0'>File</function>">
<!ENTITY FindFile "<function xmlns='http://www.scons.org/dbxsd/v1.0'>FindFile</function>">
<!ENTITY FindInstalledFiles "<function xmlns='http://www.scons.org/dbxsd/v1.0'>FindInstalledFiles</function>">
<!ENTITY FindPathDirs "<function xmlns='http://www.scons.org/dbxsd/v1.0'>FindPathDirs</function>">
<!ENTITY Finish "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Finish</function>">
<!ENTITY Flatten "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Flatten</function>">
<!ENTITY GenerateHelpText "<function xmlns='http://www.scons.org/dbxsd/v1.0'>GenerateHelpText</function>">
<!ENTITY GetBuildFailures "<function xmlns='http://www.scons.org/dbxsd/v1.0'>GetBuildFailures</function>">
<!ENTITY GetBuildPath "<function xmlns='http://www.scons.org/dbxsd/v1.0'>GetBuildPath</function>">
<!ENTITY GetLaunchDir "<function xmlns='http://www.scons.org/dbxsd/v1.0'>GetLaunchDir</function>">
<!ENTITY GetOption "<function xmlns='http://www.scons.org/dbxsd/v1.0'>GetOption</function>">
<!ENTITY Glob "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Glob</function>">
<!ENTITY Help "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Help</function>">
<!ENTITY Ignore "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Ignore</function>">
<!ENTITY Import "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Import</function>">
<!ENTITY Install "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Install</function>">
<!ENTITY InstallAs "<function xmlns='http://www.scons.org/dbxsd/v1.0'>InstallAs</function>">
<!ENTITY InstallVersionedLib "<function xmlns='http://www.scons.org/dbxsd/v1.0'>InstallVersionedLib</function>">
<!ENTITY Link "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Link</function>">
<!ENTITY ListOption "<function xmlns='http://www.scons.org/dbxsd/v1.0'>ListOption</function>">
<!ENTITY ListVariable "<function xmlns='http://www.scons.org/dbxsd/v1.0'>ListVariable</function>">
<!ENTITY Local "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Local</function>">
<!ENTITY MergeFlags "<function xmlns='http://www.scons.org/dbxsd/v1.0'>MergeFlags</function>">
<!ENTITY Mkdir "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Mkdir</function>">
<!ENTITY Module "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Module</function>">
<!ENTITY Move "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Move</function>">
<!ENTITY NoClean "<function xmlns='http://www.scons.org/dbxsd/v1.0'>NoClean</function>">
<!ENTITY NoCache "<function xmlns='http://www.scons.org/dbxsd/v1.0'>NoCache</function>">
<!ENTITY Objects "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Objects</function>">
<!ENTITY Options "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Options</function>">
<!ENTITY SConscriptFunc "<function xmlns='http://www.scons.org/dbxsd/v1.0'>SConscript</function>">
<!ENTITY Variables "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Variables</function>">
<!ENTITY PackageOption "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PackageOption</function>">
<!ENTITY PackageVariable "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PackageVariable</function>">
<!ENTITY ParseConfig "<function xmlns='http://www.scons.org/dbxsd/v1.0'>ParseConfig</function>">
<!ENTITY ParseDepends "<function xmlns='http://www.scons.org/dbxsd/v1.0'>ParseDepends</function>">
<!ENTITY ParseFlags "<function xmlns='http://www.scons.org/dbxsd/v1.0'>ParseFlags</function>">
<!ENTITY PathOption "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathOption</function>">
<!ENTITY PathOption_PathAccept "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathOption.PathAccept</function>">
<!ENTITY PathOption_PathExists "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathOption.PathExists</function>">
<!ENTITY PathOption_PathIsDir "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathOption.PathIsDir</function>">
<!ENTITY PathOption_PathIsDirCreate "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathOption.PathIsDirCreate</function>">
<!ENTITY PathOption_PathIsFile "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathOption.PathIsFile</function>">
<!ENTITY PathVariable "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathVariable</function>">
<!ENTITY PathVariable_PathAccept "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathVariable.PathAccept</function>">
<!ENTITY PathVariable_PathExists "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathVariable.PathExists</function>">
<!ENTITY PathVariable_PathIsDir "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathVariable.PathIsDir</function>">
<!ENTITY PathVariable_PathIsDirCreate "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathVariable.PathIsDirCreate</function>">
<!ENTITY PathVariable_PathIsFile "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PathVariable.PathIsFile</function>">
<!ENTITY Precious "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Precious</function>">
<!ENTITY Prepend "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Prepend</function>">
<!ENTITY PrependENVPath "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PrependENVPath</function>">
<!ENTITY PrependUnique "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PrependUnique</function>">
<!ENTITY Progress "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Progress</function>">
<!ENTITY PyPackageDir "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PyPackageDir</function>">
<!ENTITY Replace "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Replace</function>">
<!ENTITY Repository "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Repository</function>">
<!ENTITY Requires "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Requires</function>">
<!ENTITY Return "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Return</function>">
<!ENTITY RuleSet "<function xmlns='http://www.scons.org/dbxsd/v1.0'>RuleSet</function>">
<!ENTITY Salt "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Salt</function>">
<!ENTITY SetBuildSignatureType "<function xmlns='http://www.scons.org/dbxsd/v1.0'>SetBuildSignatureType</function>">
<!ENTITY SetContentSignatureType "<function xmlns='http://www.scons.org/dbxsd/v1.0'>SetContentSignatureType</function>">
<!ENTITY SetDefault "<function xmlns='http://www.scons.org/dbxsd/v1.0'>SetDefault</function>">
<!ENTITY SetOption "<function xmlns='http://www.scons.org/dbxsd/v1.0'>SetOption</function>">
<!ENTITY SideEffect "<function xmlns='http://www.scons.org/dbxsd/v1.0'>SideEffect</function>">
<!ENTITY Split "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Split</function>">
<!ENTITY Tag "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Tag</function>">
<!ENTITY Task "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Task</function>">
<!ENTITY Tool "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Tool</function>">
<!ENTITY Touch "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Touch</function>">
<!ENTITY UnknownOptions "<function xmlns='http://www.scons.org/dbxsd/v1.0'>UnknownOptions</function>">
<!ENTITY UnknownVariables "<function xmlns='http://www.scons.org/dbxsd/v1.0'>UnknownVariables</function>">

<!-- Environment methods -->
<!ENTITY subst "<function xmlns='http://www.scons.org/dbxsd/v1.0'>subst</function>">

<!-- Configure context functions -->
<!ENTITY Message "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Message</function>">
<!ENTITY Result "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Result</function>">
<!ENTITY CheckCHeader "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CheckCHeader</function>">
<!ENTITY CheckCXXHeader "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CheckCXXHeader</function>">
<!ENTITY CheckFunc "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CheckFunc</function>">
<!ENTITY CheckHeader "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CheckHeader</function>">
<!ENTITY CheckLib "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CheckLib</function>">
<!ENTITY CheckLibWithHeader "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CheckLibWithHeader</function>">
<!ENTITY CheckProg "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CheckProg</function>">
<!ENTITY CheckType "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CheckType</function>">
<!ENTITY CheckTypeSize "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CheckTypeSize</function>">
<!ENTITY TryAction "<function xmlns='http://www.scons.org/dbxsd/v1.0'>TryAction</function>">
<!ENTITY TryBuild "<function xmlns='http://www.scons.org/dbxsd/v1.0'>TryBuild</function>">
<!ENTITY TryCompile "<function xmlns='http://www.scons.org/dbxsd/v1.0'>TryCompile</function>">
<!ENTITY TryLink "<function xmlns='http://www.scons.org/dbxsd/v1.0'>TryLink</function>">
<!ENTITY TryRun "<function xmlns='http://www.scons.org/dbxsd/v1.0'>TryRun</function>">


<!-- Python functions and classes -->
<!ENTITY IndexError "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>IndexError</classname>">
<!ENTITY NameError "<classname xmlns='http://www.scons.org/dbxsd/v1.0'>NameError</classname>">
<!ENTITY str "<function xmlns='http://www.scons.org/dbxsd/v1.0'>str</function>">
<!ENTITY zipfile "<function xmlns='http://www.scons.org/dbxsd/v1.0'>zipfile</function>">

<!-- Obsolete, but referenced in old documents.  -->
<!ENTITY Cache "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Cache</function>">



<!--

  Global variables.

-->

<!ENTITY ARGLIST "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>ARGLIST</varname>">
<!ENTITY ARGUMENTS "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>ARGUMENTS</varname>">
<!ENTITY BUILD_TARGETS "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>BUILD_TARGETS</varname>">
<!ENTITY COMMAND_LINE_TARGETS "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>COMMAND_LINE_TARGETS</varname>">
<!ENTITY DEFAULT_TARGETS "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>DEFAULT_TARGETS</varname>">



<!--

  Construction variables.

-->

<!ENTITY BUILDERMAP "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>BUILDERMAP</varname>">
<!ENTITY COLOR "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>COLOR</varname>">
<!ENTITY COLORS "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>COLORS</varname>">
<!ENTITY CONFIG "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>CONFIG</varname>">
<!ENTITY CPPDEFINES "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>CPPDEFINES</varname>">
<!ENTITY RELEASE "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>RELEASE</varname>">
<!ENTITY RELEASE_BUILD "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>RELEASE_BUILD</varname>">
<!ENTITY SCANNERMAP "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>SCANNERMAP</varname>">
<!ENTITY TARFLAGS "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>TARFLAGS</varname>">
<!ENTITY TARSUFFIX "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>TARSUFFIX</varname>">



<!--

  Environment variables.

-->

<!ENTITY PATH "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>PATH</varname>">
<!ENTITY PYTHONPATH "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>PYTHONPATH</varname>">
<!ENTITY SCONSFLAGS "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>SCONSFLAGS</varname>">



<!--

  Function and method arguments.

-->

<!ENTITY allowed_values "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>allowed_values</varname>">
<!ENTITY build_dir "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>build_dir</varname>">
<!ENTITY map "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>map</varname>">
<!ENTITY ignorecase "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>ignorecase</varname>">
<!ENTITY options "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>options</varname>">
<!ENTITY exports "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>exports</varname>">
<!ENTITY source "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>source</varname>">
<!ENTITY target "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>target</varname>">
<!ENTITY variables "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>variables</varname>">
<!ENTITY variant_dir "<varname xmlns='http://www.scons.org/dbxsd/v1.0'>variant_dir</varname>">



<!--

  Values of function and method arguments.

-->

<!ENTITY all "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>all</literal>">
<!ENTITY none "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>none</literal>">



<!--

  Builder and Scanner objects.

-->

<!ENTITY BuildDir "<function xmlns='http://www.scons.org/dbxsd/v1.0'>BuildDir</function>">
<!ENTITY CFile "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CFile</function>">
<!ENTITY CXXFile "<function xmlns='http://www.scons.org/dbxsd/v1.0'>CXXFile</function>">
<!ENTITY DVI "<function xmlns='http://www.scons.org/dbxsd/v1.0'>DVI</function>">
<!ENTITY Jar "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Jar</function>">
<!ENTITY Java "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Java</function>">
<!ENTITY JavaH "<function xmlns='http://www.scons.org/dbxsd/v1.0'>JavaH</function>">
<!ENTITY Library "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Library</function>">
<!ENTITY Object "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Object</function>">
<!ENTITY PCH "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PCH</function>">
<!ENTITY PDF "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PDF</function>">
<!ENTITY PostScript "<function xmlns='http://www.scons.org/dbxsd/v1.0'>PostScript</function>">
<!ENTITY Program "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Program</function>">
<!ENTITY RES "<function xmlns='http://www.scons.org/dbxsd/v1.0'>RES</function>">
<!ENTITY RMIC "<function xmlns='http://www.scons.org/dbxsd/v1.0'>RMIC</function>">
<!ENTITY SharedLibrary "<function xmlns='http://www.scons.org/dbxsd/v1.0'>SharedLibrary</function>">
<!ENTITY SharedObject "<function xmlns='http://www.scons.org/dbxsd/v1.0'>SharedObject</function>">
<!ENTITY StaticLibrary "<function xmlns='http://www.scons.org/dbxsd/v1.0'>StaticLibrary</function>">
<!ENTITY StaticObject "<function xmlns='http://www.scons.org/dbxsd/v1.0'>StaticObject</function>">
<!ENTITY Substfile "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Substfile</function>">
<!ENTITY Tar "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Tar</function>">
<!ENTITY Textfile "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Textfile</function>">
<!ENTITY VariantDir "<function xmlns='http://www.scons.org/dbxsd/v1.0'>VariantDir</function>">
<!ENTITY Zip "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Zip</function>">

<!-- Obsolete, but referenced in old documents.  -->
<!ENTITY MakeBuilder "<function xmlns='http://www.scons.org/dbxsd/v1.0'>Make</function>">



<!--

  Terms.  Define both singular and plural forms in various
  case-sensitive combinations for use in titles, in-line, etc.

-->

<!ENTITY buildfunc "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>builder function</phrase>">
<!ENTITY build_action "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>build action</phrase>">
<!ENTITY build_actions "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>build actions</phrase>">
<!ENTITY builder_method "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>builder method</phrase>">

<!ENTITY Configure_Contexts "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Configure Contexts</phrase>">
<!ENTITY configure_context "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>configure context</phrase>">

<!ENTITY ConsEnv "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Construction Environment</phrase>">
<!ENTITY ConsEnvs "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Construction Environments</phrase>">
<!ENTITY Consenv "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Construction environment</phrase>">
<!ENTITY Consenvs "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Construction environments</phrase>">
<!ENTITY consenv "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>construction environment</phrase>">
<!ENTITY consenvs "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>construction environments</phrase>">
<!ENTITY DefEnv "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Default Environment</phrase>">
<!ENTITY defenv "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>default environment</phrase>">

<!ENTITY ConsVar "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Construction Variable</phrase>">
<!ENTITY ConsVars "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Construction Variables</phrase>">
<!ENTITY Consvar "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Construction variable</phrase>">
<!ENTITY Consvars "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>Construction variables</phrase>">
<!ENTITY consvar "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>construction variable</phrase>">
<!ENTITY consvars "<phrase xmlns='http://www.scons.org/dbxsd/v1.0'>construction variables</phrase>">

<!ENTITY CPPPATH "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>CPPPATH</literal>">

<!ENTITY Dictionary "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>Dictionary</literal>">

<!ENTITY Emitter "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>Emitter</literal>">
<!ENTITY emitter "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>emitter</literal>">

<!ENTITY factory "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>factory</literal>">

<!ENTITY Generator "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>Generator</literal>">
<!ENTITY generator "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>generator</literal>">

<!ENTITY Nodes "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>Nodes</literal>">

<!ENTITY signature "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>signature</literal>">
<!ENTITY buildsignature "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>build signature</literal>">

<!ENTITY true "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>true</literal>">
<!ENTITY false "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>false</literal>">

<!ENTITY typedef "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>typedef</literal>">

<!--

  Python keyword arguments

-->

<!ENTITY action "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>action=</literal>">
<!ENTITY batch_key "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>batch_key=</literal>">
<!ENTITY cmdstr "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>cmdstr=</literal>">
<!ENTITY exitstatfunc "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>exitstatfunc=</literal>">
<!ENTITY strfunction "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>strfunction=</literal>">
<!ENTITY varlist "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>varlist=</literal>">

<!--

  File and program names used in examples.

-->

<!ENTITY bar "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>bar</filename>">
<!ENTITY common1_c "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>common1.c</filename>">
<!ENTITY common2_c "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>common2.c</filename>">
<!ENTITY custom_py "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>custom.py</filename>">
<!ENTITY goodbye "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>goodbye</filename>">
<!ENTITY goodbye_o "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>goodbye.o</filename>">
<!ENTITY goodbye_obj "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>goodbye.obj</filename>">
<!ENTITY file_dll "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>file.dll</filename>">
<!ENTITY file_in "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>file.in</filename>">
<!ENTITY file_lib "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>file.lib</filename>">
<!ENTITY file_o "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>file.o</filename>">
<!ENTITY file_obj "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>file.obj</filename>">
<!ENTITY file_out "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>file.out</filename>">
<!ENTITY foo "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>foo</filename>">
<!ENTITY foo_o "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>foo.o</filename>">
<!ENTITY foo_obj "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>foo.obj</filename>">
<!ENTITY hello "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>hello</filename>">
<!ENTITY hello_c "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>hello.c</filename>">
<!ENTITY hello_exe "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>hello.exe</filename>">
<!ENTITY hello_h "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>hello.h</filename>">
<!ENTITY hello_o "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>hello.o</filename>">
<!ENTITY hello_obj "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>hello.obj</filename>">
<!ENTITY libfile_a "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>libfile_a</filename>">
<!ENTITY libfile_so "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>libfile_so</filename>">
<!ENTITY new_hello "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>new_hello</filename>">
<!ENTITY new_hello_exe "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>new_hello.exe</filename>">
<!ENTITY prog "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>prog</filename>">
<!ENTITY prog1 "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>prog1</filename>">
<!ENTITY prog2 "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>prog2</filename>">
<!ENTITY prog_c "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>prog.c</filename>">
<!ENTITY prog_exe "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>prog.exe</filename>">
<!ENTITY stdio_h "<filename xmlns='http://www.scons.org/dbxsd/v1.0'>stdio.h</filename>">

<!--

  Punctuation.

-->

<!ENTITY plus "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>+</literal>">
<!ENTITY hash "<literal xmlns='http://www.scons.org/dbxsd/v1.0'>#</literal>">

<!--

  Mailing lists

-->

<!ENTITY scons-announce "<email xmlns='http://www.scons.org/dbxsd/v1.0'>announce@scons.tigris.org</email>">
<!ENTITY scons-devel "<email xmlns='http://www.scons.org/dbxsd/v1.0'>scons-dev@scons.org</email>">
<!ENTITY scons-users "<email xmlns='http://www.scons.org/dbxsd/v1.0'>scons-users@scons.org</email>">

<!--

  Character entities

-->

<!ENTITY lambda "&#923;">
<!ENTITY mdash "&#8212;">
