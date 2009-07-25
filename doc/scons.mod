<!--

  __COPYRIGHT__

  An SCons-specific DTD module, for use with SCons DocBook
  documentation, that contains names, phrases, acronyms, etc. used
  throughout the SCons documentation.

-->



<!--

  Other applications that we reference.

-->

<!ENTITY Aegis          "<application>Aegis</application>">
<!ENTITY Ant            "<application>Ant</application>">
<!ENTITY ar             "<application>ar</application>">
<!ENTITY as             "<application>as</application>">
<!ENTITY Autoconf       "<application>Autoconf</application>">
<!ENTITY Automake       "<application>Automake</application>">
<!ENTITY bison          "<application>bison</application>">
<!ENTITY cc             "<application>cc</application>">
<!ENTITY Cons           "<application>Cons</application>">
<!ENTITY cp             "<application>cp</application>">
<!ENTITY csh            "<application>csh</application>">
<!ENTITY f77            "<application>f77</application>">
<!ENTITY f90            "<application>f90</application>">
<!ENTITY f95            "<application>f95</application>">
<!ENTITY gas            "<application>gas</application>">
<!ENTITY gcc            "<application>gcc</application>">
<!ENTITY g77            "<application>g77</application>">
<!ENTITY gXX            "<application>gXX</application>">
<!ENTITY Jam            "<application>Jam</application>">
<!ENTITY jar            "<application>jar</application>">
<!ENTITY javac          "<application>javac</application>">
<!ENTITY javah          "<application>javah</application>">
<!ENTITY latex          "<application>latex</application>">
<!ENTITY lex            "<application>lex</application>">
<!ENTITY m4             "<application>m4</application>">
<!ENTITY Make           "<application>Make</application>">
<!ENTITY Makepp         "<application>Make++</application>">
<!ENTITY pdflatex       "<application>pdflatex</application>">
<!ENTITY pdftex         "<application>pdftex</application>">
<!ENTITY Python         "<application>Python</application>">
<!ENTITY ranlib         "<application>ranlib</application>">
<!ENTITY rmic           "<application>rmic</application>">
<!ENTITY SCons          "<application>SCons</application>">
<!ENTITY ScCons         "<application>ScCons</application>">
<!ENTITY swig           "<application>swig</application>">
<!ENTITY tar            "<application>tar</application>">
<!ENTITY tex            "<application>tex</application>">
<!ENTITY touch          "<application>touch</application>">
<!ENTITY yacc           "<application>yacc</application>">
<!ENTITY zip            "<application>zip</application>">


<!--

  Classes.

-->

<!ENTITY Action "<classname>Action</classname>">
<!ENTITY ActionBase "<classname>ActionBase</classname>">
<!ENTITY CommandAction "<classname>CommandAction</classname>">
<!ENTITY FunctionAction "<classname>FunctionAction</classname>">
<!ENTITY ListAction "<classname>ListAction</classname>">
<!ENTITY Builder "<classname>Builder</classname>">
<!ENTITY BuilderBase "<classname>BuilderBase</classname>">
<!ENTITY CompositeBuilder "<classname>CompositeBuilder</classname>">
<!ENTITY MultiStepBuilder "<classname>MultiStepBuilder</classname>">
<!ENTITY Job "<classname>Job</classname>">
<!ENTITY Jobs "<classname>Jobs</classname>">
<!ENTITY Serial "<classname>Serial</classname>">
<!ENTITY Parallel "<classname>Parallel</classname>">
<!ENTITY Node "<classname>Node</classname>">
<!ENTITY Node_FS "<classname>Node.FS</classname>">
<!ENTITY Scanner "<classname>Scanner</classname>">
<!ENTITY Sig "<classname>Sig</classname>">
<!ENTITY Signature "<classname>Signature</classname>">
<!ENTITY Taskmaster "<classname>Taskmaster</classname>">
<!ENTITY TimeStamp "<classname>TimeStamp</classname>">
<!ENTITY Walker "<classname>Walker</classname>">
<!ENTITY Wrapper "<classname>Wrapper</classname>">



<!--

  Options, command-line.

-->

<!ENTITY config "<literal>--config</literal>">
<!ENTITY debug-explain "<literal>--debug=explain</literal>">
<!ENTITY debug-findlibs "<literal>--debug=findlibs</literal>">
<!ENTITY debug-includes "<literal>--debug=includes</literal>">
<!ENTITY debug-presub "<literal>--debug=presub</literal>">
<!ENTITY debug-stacktrace "<literal>--debug=stacktrace</literal>">
<!ENTITY implicit-cache "<literal>--implicit-cache</literal>">
<!ENTITY implicit-deps-changed "<literal>--implicit-deps-changed</literal>">
<!ENTITY implicit-deps-unchanged "<literal>--implicit-deps-unchanged</literal>">
<!ENTITY profile "<literal>--profile</literal>">
<!ENTITY taskmastertrace "<literal>--taskmastertrace</literal>">
<!ENTITY tree "<literal>--tree</literal>">
<!ENTITY Q "<literal>-Q</literal>">

<!--

  Options, SConscript-settable.

-->

<!ENTITY implicit_cache "<literal>implicit_cache</literal>">
<!ENTITY implicit_deps_changed "<literal>implicit_deps_changed</literal>">
<!ENTITY implicit_deps_unchanged "<literal>implicit_deps_unchanged</literal>">



<!--

  File and directory names.

-->

<!ENTITY build "<filename>build</filename>">
<!ENTITY Makefile "<filename>Makefile</filename>">
<!ENTITY Makefiles "<filename>Makefiles</filename>">
<!ENTITY scons "<filename>scons</filename>">
<!ENTITY SConscript "<filename>SConscript</filename>">
<!ENTITY SConstruct "<filename>SConstruct</filename>">
<!ENTITY Sconstruct "<filename>Sconstruct</filename>">
<!ENTITY sconstruct "<filename>sconstruct</filename>">
<!ENTITY sconsign "<filename>.sconsign</filename>">
<!ENTITY src "<filename>src</filename>">



<!--

  Methods and functions.  This includes functions from both
  the Build Engine and the Native Python Interface.

-->

<!ENTITY Add "<function>Add</function>">
<!ENTITY AddMethod "<function>AddMethod</function>">
<!ENTITY AddPostAction "<function>AddPostAction</function>">
<!ENTITY AddPreAction "<function>AddPreAction</function>">
<!ENTITY AddOption "<function>AddOption</function>">
<!ENTITY AddOptions "<function>AddOptions</function>">
<!ENTITY AddVariables "<function>AddVariables</function>">
<!ENTITY Alias "<function>Alias</function>">
<!ENTITY Aliases "<function>Aliases</function>">
<!ENTITY AlwaysBuild "<function>AlwaysBuild</function>">
<!ENTITY Append "<function>Append</function>">
<!ENTITY AppendENVPath "<function>AppendENVPath</function>">
<!ENTITY AppendUnique "<function>AppendUnique</function>">
<!ENTITY BoolOption "<function>BoolOption</function>">
<!ENTITY BoolVariable "<function>BoolVariable</function>">
<!ENTITY Build "<function>Build</function>">
<!ENTITY CacheDir "<function>CacheDir</function>">
<!ENTITY Chmod "<function>Chmod</function>">
<!ENTITY Clean "<function>Clean</function>">
<!ENTITY Clone "<function>Clone</function>">
<!ENTITY Command "<function>Command</function>">
<!ENTITY Configure "<function>Configure</function>">
<!ENTITY Copy "<function>Copy</function>">
<!ENTITY Decider "<function>Decider</function>">
<!ENTITY Default "<function>Default</function>">
<!ENTITY DefaultEnvironment "<function>DefaultEnvironment</function>">
<!ENTITY DefaultRules "<function>DefaultRules</function>">
<!ENTITY Delete "<function>Delete</function>">
<!ENTITY Depends "<function>Depends</function>">
<!ENTITY Dir "<function>Dir</function>">
<!ENTITY Dump "<function>Dump</function>">
<!ENTITY Entry "<function>Entry</function>">
<!ENTITY EnumOption "<function>EnumOption</function>">
<!ENTITY EnumVariable "<function>EnumVariable</function>">
<!ENTITY EnsurePythonVersion "<function>EnsurePythonVersion</function>">
<!ENTITY EnsureSConsVersion "<function>EnsureSConsVersion</function>">
<!ENTITY Environment "<function>Environment</function>">
<!ENTITY Execute "<function>Execute</function>">
<!ENTITY Exit "<function>Exit</function>">
<!ENTITY Export "<function>Export</function>">
<!ENTITY File "<function>File</function>">
<!ENTITY FindFile "<function>FindFile</function>">
<!ENTITY FindInstalledFiles "<function>FindInstalledFiles</function>">
<!ENTITY Finish "<function>Finish</function>">
<!ENTITY Flatten "<function>Flatten</function>">
<!ENTITY GenerateHelpText "<function>GenerateHelpText</function>">
<!ENTITY GetBuildFailures "<function>GetBuildFailures</function>">
<!ENTITY GetLaunchDir "<function>GetLaunchDir</function>">
<!ENTITY GetOption "<function>GetOption</function>">
<!ENTITY Glob "<function>Glob</function>">
<!ENTITY Help "<function>Help</function>">
<!ENTITY Ignore "<function>Ignore</function>">
<!ENTITY Import "<function>Import</function>">
<!ENTITY Install "<function>Install</function>">
<!ENTITY InstallAs "<function>InstallAs</function>">
<!ENTITY Link "<function>Link</function>">
<!ENTITY ListOption "<function>ListOption</function>">
<!ENTITY ListVariable "<function>ListVariable</function>">
<!ENTITY Local "<function>Local</function>">
<!ENTITY MergeFlags "<function>MergeFlags</function>">
<!ENTITY Mkdir "<function>Mkdir</function>">
<!ENTITY Module "<function>Module</function>">
<!ENTITY Move "<function>Move</function>">
<!ENTITY NoClean "<function>NoClean</function>">
<!ENTITY NoCache "<function>NoCache</function>">
<!ENTITY Objects "<function>Objects</function>">
<!ENTITY Options "<function>Options</function>">
<!ENTITY Variables "<function>Variables</function>">
<!ENTITY PackageOption "<function>PackageOption</function>">
<!ENTITY PackageVariable "<function>PackageVariable</function>">
<!ENTITY ParseConfig "<function>ParseConfig</function>">
<!ENTITY ParseDepends "<function>ParseDepends</function>">
<!ENTITY ParseFlags "<function>ParseFlags</function>">
<!ENTITY PathOption "<function>PathOption</function>">
<!ENTITY PathOption_PathAccept "<function>PathOption.PathAccept</function>">
<!ENTITY PathOption_PathExists "<function>PathOption.PathExists</function>">
<!ENTITY PathOption_PathIsDir "<function>PathOption.PathIsDir</function>">
<!ENTITY PathOption_PathIsDirCreate "<function>PathOption.PathIsDirCreate</function>">
<!ENTITY PathOption_PathIsFile "<function>PathOption.PathIsFile</function>">
<!ENTITY PathVariable "<function>PathVariable</function>">
<!ENTITY PathVariable_PathAccept "<function>PathVariable.PathAccept</function>">
<!ENTITY PathVariable_PathExists "<function>PathVariable.PathExists</function>">
<!ENTITY PathVariable_PathIsDir "<function>PathVariable.PathIsDir</function>">
<!ENTITY PathVariable_PathIsDirCreate "<function>PathVariable.PathIsDirCreate</function>">
<!ENTITY PathVariable_PathIsFile "<function>PathVariable.PathIsFile</function>">
<!ENTITY Precious "<function>Precious</function>">
<!ENTITY Prepend "<function>Prepend</function>">
<!ENTITY PrependENVPath "<function>PrependENVPath</function>">
<!ENTITY PrependUnique "<function>PrependUnique</function>">
<!ENTITY Progress "<function>Progress</function>">
<!ENTITY Replace "<function>Replace</function>">
<!ENTITY Repository "<function>Repository</function>">
<!ENTITY Requires "<function>Requires</function>">
<!ENTITY Return "<function>Return</function>">
<!ENTITY RuleSet "<function>RuleSet</function>">
<!ENTITY Salt "<function>Salt</function>">
<!ENTITY SetBuildSignatureType "<function>SetBuildSignatureType</function>">
<!ENTITY SetContentSignatureType "<function>SetContentSignatureType</function>">
<!ENTITY SetDefault "<function>SetDefault</function>">
<!ENTITY SetOption "<function>SetOption</function>">
<!ENTITY SideEffect "<function>SideEffect</function>">
<!ENTITY SourceSignature "<function>SourceSignature</function>">
<!ENTITY SourceSignatures "<function>SourceSignatures</function>">
<!ENTITY Split "<function>Split</function>">
<!ENTITY Tag "<function>Tag</function>">
<!ENTITY TargetSignatures "<function>TargetSignatures</function>">
<!ENTITY Task "<function>Task</function>">
<!ENTITY Touch "<function>Touch</function>">
<!ENTITY UnknownOptions "<function>UnknownOptions</function>">
<!ENTITY UnknownVariables "<function>UnknownVariables</function>">

<!-- Environment methods -->
<!ENTITY subst "<function>subst</function>">

<!-- Configure context functions -->
<!ENTITY Message "<function>Message</function>">
<!ENTITY Result "<function>Result</function>">
<!ENTITY CheckCHeader "<function>CheckCHeader</function>">
<!ENTITY CheckCXXHeader "<function>CheckCXXHeader</function>">
<!ENTITY CheckFunc "<function>CheckFunc</function>">
<!ENTITY CheckHeader "<function>CheckHeader</function>">
<!ENTITY CheckLib "<function>CheckLib</function>">
<!ENTITY CheckLibWithHeader "<function>CheckLibWithHeader</function>">
<!ENTITY CheckType "<function>CheckType</function>">
<!ENTITY TryAction "<function>TryAction</function>">
<!ENTITY TryBuild "<function>TryBuild</function>">
<!ENTITY TryCompile "<function>TryCompile</function>">
<!ENTITY TryLink "<function>TryLink</function>">
<!ENTITY TryRun "<function>TryRun</function>">


<!-- Python functions -->
<!ENTITY str "<function>str</function>">
<!ENTITY zipfile "<function>zipfile</function>">

<!-- Obsolete, but referenced in old documents.  -->
<!ENTITY Cache "<function>Cache</function>">



<!--

  Global variables.

-->

<!ENTITY ARGLIST "<varname>ARGLIST</varname>">
<!ENTITY ARGUMENTS "<varname>ARGUMENTS</varname>">
<!ENTITY BUILD_TARGETS "<varname>BUILD_TARGETS</varname>">
<!ENTITY COMMAND_LINE_TARGETS "<varname>COMMAND_LINE_TARGETS</varname>">
<!ENTITY DEFAULT_TARGETS "<varname>DEFAULT_TARGETS</varname>">



<!--

  Construction variables.

-->

<!ENTITY BUILDERMAP "<varname>BUILDERMAP</varname>">
<!ENTITY COLOR "<varname>COLOR</varname>">
<!ENTITY COLORS "<varname>COLORS</varname>">
<!ENTITY CONFIG "<varname>CONFIG</varname>">
<!ENTITY CPPDEFINES "<varname>CPPDEFINES</varname>">
<!ENTITY RELEASE "<varname>RELEASE</varname>">
<!ENTITY RELEASE_BUILD "<varname>RELEASE_BUILD</varname>">
<!ENTITY SCANNERMAP "<varname>SCANNERMAP</varname>">
<!ENTITY TARFLAGS "<varname>TARFLAGS</varname>">
<!ENTITY TARSUFFIX "<varname>TARSUFFIX</varname>">



<!--

  Environment variables.

-->

<!ENTITY PATH "<varname>PATH</varname>">
<!ENTITY PYTHONPATH "<varname>PYTHONPATH</varname>">
<!ENTITY SCONSFLAGS "<varname>SCONSFLAGS</varname>">



<!--

  Function and method arguments.

-->

<!ENTITY allowed_values "<varname>allowed_values</varname>">
<!ENTITY build_dir "<varname>build_dir</varname>">
<!ENTITY map "<varname>map</varname>">
<!ENTITY ignorecase "<varname>ignorecase</varname>">
<!ENTITY options "<varname>options</varname>">
<!ENTITY exports "<varname>exports</varname>">
<!ENTITY source "<varname>source</varname>">
<!ENTITY target "<varname>target</varname>">
<!ENTITY variables "<varname>variables</varname>">
<!ENTITY variant_dir "<varname>variant_dir</varname>">



<!--

  Values of function and method arguments.

-->

<!ENTITY all "<literal>all</literal>">
<!ENTITY none "<literal>none</literal>">



<!--

  Builder and Scanner objects.

-->

<!ENTITY BuildDir "<function>BuildDir</function>">
<!ENTITY CFile "<function>CFile</function>">
<!ENTITY CXXFile "<function>CXXFile</function>">
<!ENTITY DVI "<function>DVI</function>">
<!ENTITY Jar "<function>Jar</function>">
<!ENTITY Java "<function>Java</function>">
<!ENTITY JavaH "<function>JavaH</function>">
<!ENTITY Library "<function>Library</function>">
<!ENTITY Object "<function>Object</function>">
<!ENTITY PCH "<function>PCH</function>">
<!ENTITY PDF "<function>PDF</function>">
<!ENTITY PostScript "<function>PostScript</function>">
<!ENTITY Program "<function>Program</function>">
<!ENTITY RES "<function>RES</function>">
<!ENTITY RMIC "<function>RMIC</function>">
<!ENTITY SharedLibrary "<function>SharedLibrary</function>">
<!ENTITY SharedObject "<function>SharedObject</function>">
<!ENTITY StaticLibrary "<function>StaticLibrary</function>">
<!ENTITY StaticObject "<function>StaticObject</function>">
<!ENTITY Substfile "<function>Substfile</function>">
<!ENTITY Tar "<function>Tar</function>">
<!ENTITY Textfile "<function>Textfile</function>">
<!ENTITY VariantDir "<function>VariantDir</function>">
<!ENTITY Zip "<function>Zip</function>">

<!-- Obsolete, but referenced in old documents.  -->
<!ENTITY MakeBuilder "<function>Make</function>">



<!--

  Terms.  Define both singular and plural forms in various
  case-sensitive combinations for use in titles, in-line, etc.

-->

<!ENTITY buildfunc "<literal>builder function</literal>">
<!ENTITY build_action "<literal>build action</literal>">
<!ENTITY build_actions "<literal>build actions</literal>">
<!ENTITY builder_method "<literal>builder method</literal>">

<!ENTITY Configure_Contexts "<literal>Configure Contexts</literal>">
<!ENTITY configure_context "<literal>configure context</literal>">

<!ENTITY ConsEnv "<literal>Construction Environment</literal>">
<!ENTITY ConsEnvs "<literal>Construction Environments</literal>">
<!ENTITY Consenv "<literal>Construction environment</literal>">
<!ENTITY Consenvs "<literal>Construction environments</literal>">
<!ENTITY consenv "<literal>construction environment</literal>">
<!ENTITY consenvs "<literal>construction environments</literal>">

<!ENTITY ConsVar "<literal>Construction Variable</literal>">
<!ENTITY ConsVars "<literal>Construction Variables</literal>">
<!ENTITY Consvar "<literal>Construction variable</literal>">
<!ENTITY Consvars "<literal>Construction variables</literal>">
<!ENTITY consvar "<literal>construction variable</literal>">
<!ENTITY consvars "<literal>construction variables</literal>">

<!ENTITY CPPPATH "<literal>CPPPATH</literal>">

<!ENTITY Dictionary "<literal>Dictionary</literal>">

<!ENTITY Emitter "<literal>Emitter</literal>">
<!ENTITY emitter "<literal>emitter</literal>">

<!ENTITY factory "<literal>factory</literal>">

<!ENTITY Generator "<literal>Generator</literal>">
<!ENTITY generator "<literal>generator</literal>">

<!ENTITY Nodes "<literal>Nodes</literal>">

<!ENTITY signature "<literal>signature</literal>">
<!ENTITY buildsignature "<literal>build signature</literal>">

<!ENTITY true "<literal>true</literal>">
<!ENTITY false "<literal>false</literal>">

<!ENTITY typedef "<literal>typedef</literal>">

<!--

  Python keyword arguments

-->

<!ENTITY action "<literal>action=</literal>">
<!ENTITY batch_key "<literal>batch_key=</literal>">
<!ENTITY cmdstr "<literal>cmdstr=</literal>">
<!ENTITY exitstatfunc "<literal>exitstatfunc=</literal>">
<!ENTITY strfunction "<literal>strfunction=</literal>">
<!ENTITY varlist "<literal>varlist=</literal>">

<!--

  File and program names used in examples.

-->

<!ENTITY bar "<filename>bar</filename>">
<!ENTITY common1_c "<filename>common1.c</filename>">
<!ENTITY common2_c "<filename>common2.c</filename>">
<!ENTITY custom_py "<filename>custom.py</filename>">
<!ENTITY goodbye "<filename>goodbye</filename>">
<!ENTITY goodbye_o "<filename>goodbye.o</filename>">
<!ENTITY goodbye_obj "<filename>goodbye.obj</filename>">
<!ENTITY file_dll "<filename>file.dll</filename>">
<!ENTITY file_in "<filename>file.in</filename>">
<!ENTITY file_lib "<filename>file.lib</filename>">
<!ENTITY file_o "<filename>file.o</filename>">
<!ENTITY file_obj "<filename>file.obj</filename>">
<!ENTITY file_out "<filename>file.out</filename>">
<!ENTITY foo "<filename>foo</filename>">
<!ENTITY foo_o "<filename>foo.o</filename>">
<!ENTITY foo_obj "<filename>foo.obj</filename>">
<!ENTITY hello "<filename>hello</filename>">
<!ENTITY hello_c "<filename>hello.c</filename>">
<!ENTITY hello_exe "<filename>hello.exe</filename>">
<!ENTITY hello_h "<filename>hello.h</filename>">
<!ENTITY hello_o "<filename>hello.o</filename>">
<!ENTITY hello_obj "<filename>hello.obj</filename>">
<!ENTITY libfile_a "<filename>libfile_a</filename>">
<!ENTITY libfile_so "<filename>libfile_so</filename>">
<!ENTITY new_hello "<filename>new_hello</filename>">
<!ENTITY new_hello_exe "<filename>new_hello.exe</filename>">
<!ENTITY prog "<filename>prog</filename>">
<!ENTITY prog1 "<filename>prog1</filename>">
<!ENTITY prog2 "<filename>prog2</filename>">
<!ENTITY prog_c "<filename>prog.c</filename>">
<!ENTITY prog_exe "<filename>prog.exe</filename>">
<!ENTITY stdio_h "<filename>stdio.h</filename>">

<!--

  Punctuation.

-->

<!ENTITY plus "<literal>+</literal>">
<!ENTITY hash "<literal>#</literal>">

<!--

  Mailing lists

-->

<!ENTITY scons-announce "<literal>announce@scons.tigris.org</literal>">
<!ENTITY scons-devel "<literal>dev@scons.tigris.org</literal>">
<!ENTITY scons-users "<literal>users@scons.tigris.org</literal>">
