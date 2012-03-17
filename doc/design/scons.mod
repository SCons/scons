<!--

  __COPYRIGHT__

  An SCons-specific DTD module, for use with SCons DocBook
  documentation, that contains names, phrases, acronyms, etc. used
  throughout the SCons documentation.

-->



<!--

  Other applications that we reference.

-->

<!ENTITY Aegis "<application>Aegis</application>">
<!ENTITY Ant "<application>Ant</application>">
<!ENTITY Autoconf "<application>Autoconf</application>">
<!ENTITY Automake "<application>Automake</application>">
<!ENTITY cc "<application>cc</application>">
<!ENTITY Cons "<application>Cons</application>">
<!ENTITY cp "<application>cp</application>">
<!ENTITY csh "<application>csh</application>">
<!ENTITY gcc "<application>gcc</application>">
<!ENTITY Jam "<application>Jam</application>">
<!ENTITY jar "<application>jar</application>">
<!ENTITY javac "<application>javac</application>">
<!ENTITY javah "<application>javah</application>">
<!ENTITY Make "<application>Make</application>">
<!ENTITY Makepp "<application>Make++</application>">
<!ENTITY Python "<application>Python</application>">
<!ENTITY ranlib "<application>ranlib</application>">
<!ENTITY rmic "<application>rmic</application>">
<!ENTITY SCons "<application>SCons</application>">
<!ENTITY scons "<application>scons</application>">
<!ENTITY ScCons "<application>ScCons</application>">
<!ENTITY tar "<application>tar</application>">
<!ENTITY touch "<application>touch</application>">
<!ENTITY zip "<application>zip</application>">


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

<!ENTITY debug-explain "<literal>--debug=explain</literal>">
<!ENTITY implicit-cache "<literal>--implicit-cache</literal>">
<!ENTITY implicit-deps-changed "<literal>--implicit-deps-changed</literal>">
<!ENTITY implicit-deps-unchanged "<literal>--implicit-deps-unchanged</literal>">
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
<!ENTITY AddOptions "<function>AddOptions</function>">
<!ENTITY Alias "<function>Alias</function>">
<!ENTITY Aliases "<function>Aliases</function>">
<!ENTITY Append "<function>Append</function>">
<!ENTITY BoolOption "<function>BoolOption</function>">
<!ENTITY Build "<function>Build</function>">
<!ENTITY CacheDir "<function>CacheDir</function>">
<!ENTITY Clean "<function>Clean</function>">
<!ENTITY Clone "<function>Clone</function>">
<!ENTITY Command "<function>Command</function>">
<!ENTITY Configure "<function>Configure</function>">
<!ENTITY Copy "<function>Copy</function>">
<!ENTITY Default "<function>Default</function>">
<!ENTITY DefaultRules "<function>DefaultRules</function>">
<!ENTITY Depends "<function>Depends</function>">
<!ENTITY Dir "<function>Dir</function>">
<!ENTITY Entry "<function>Entry</function>">
<!ENTITY EnumOption "<function>EnumOption</function>">
<!ENTITY Environment "<function>Environment</function>">
<!ENTITY Export "<function>Export</function>">
<!ENTITY File "<function>File</function>">
<!ENTITY Finish "<function>Finish</function>">
<!ENTITY GenerateHelpText "<function>GenerateHelpText</function>">
<!ENTITY Help "<function>Help</function>">
<!ENTITY Ignore "<function>Ignore</function>">
<!ENTITY Import "<function>Import</function>">
<!ENTITY Install "<function>Install</function>">
<!ENTITY InstallAs "<function>InstallAs</function>">
<!ENTITY Link "<function>Link</function>">
<!ENTITY ListOption "<function>ListOption</function>">
<!ENTITY Local "<function>Local</function>">
<!ENTITY Module "<function>Module</function>">
<!ENTITY NoClean "<function>NoClean</function>">
<!ENTITY Objects "<function>Objects</function>">
<!ENTITY Options "<function>Options</function>">
<!ENTITY PackageOption "<function>PackageOption</function>">
<!ENTITY PathOption "<function>PathOption</function>">
<!ENTITY Precious "<function>Precious</function>">
<!ENTITY Prepend "<function>Prepend</function>">
<!ENTITY Replace "<function>Replace</function>">
<!ENTITY Repository "<function>Repository</function>">
<!ENTITY Return "<function>Return</function>">
<!ENTITY RuleSet "<function>RuleSet</function>">
<!ENTITY Salt "<function>Salt</function>">
<!ENTITY SetBuildSignatureType "<function>SetBuildSignatureType</function>">
<!ENTITY SetContentSignatureType "<function>SetContentSignatureType</function>">
<!ENTITY SourceSignature "<function>SourceSignature</function>">
<!ENTITY SourceSignatures "<function>SourceSignatures</function>">
<!ENTITY Split "<function>Split</function>">
<!ENTITY TargetSignatures "<function>TargetSignatures</function>">
<!ENTITY Task "<function>Task</function>">

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

<!ENTITY ARGUMENTS "<varname>ARGUMENTS</varname>">
<!ENTITY BUILD_TARGETS "<varname>BUILD_TARGETS</varname>">
<!ENTITY COMMAND_LINE_TARGETS "<varname>COMMAND_LINE_TARGETS</varname>">
<!ENTITY DEFAULT_TARGETS "<varname>DEFAULT_TARGETS</varname>">



<!--

  Construction variables.

-->

<!ENTITY BUILDERMAP "<varname>BUILDERMAP</varname>">
<!ENTITY BUILDERS "<varname>BUILDERS</varname>">
<!ENTITY CC "<varname>CC</varname>">
<!ENTITY CCFLAGS "<varname>CCFLAGS</varname>">
<!ENTITY CCCOM "<varname>CCCOM</varname>">
<!ENTITY COLOR "<varname>COLOR</varname>">
<!ENTITY COLORS "<varname>COLORS</varname>">
<!ENTITY CONFIG "<varname>CONFIG</varname>">
<!ENTITY CPPDEFINES "<varname>CPPDEFINES</varname>">
<!ENTITY ENV "<varname>ENV</varname>">
<!ENTITY JAVACLASSDIR "<varname>JAVACLASSDIR</varname>">
<!ENTITY LIBDIRPREFIX "<varname>LIBDIRPREFIX</varname>">
<!ENTITY LIBDIRSUFFIX "<varname>LIBDIRSUFFIX</varname>">
<!ENTITY LIBLINKPREFIX "<varname>LIBLINKPREFIX</varname>">
<!ENTITY LIBLINKSUFFIX "<varname>LIBLINKSUFFIX</varname>">
<!ENTITY LIBPATH "<varname>LIBPATH</varname>">
<!ENTITY LIBS "<varname>LIBS</varname>">
<!ENTITY LINK "<varname>LINK</varname>">
<!ENTITY LINKCOM "<varname>LINKCOM</varname>">
<!ENTITY LINKFLAGS "<varname>LINKFLAGS</varname>">
<!ENTITY RELEASE "<varname>RELEASE</varname>">
<!ENTITY RELEASE_BUILD "<varname>RELEASE_BUILD</varname>">
<!ENTITY SCANNERMAP "<varname>SCANNERMAP</varname>">
<!ENTITY SCANNERS "<varname>SCANNERS</varname>">
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
<!ENTITY Tar "<function>Tar</function>">
<!ENTITY Zip "<function>Zip</function>">

<!-- Obsolete, but referenced in old documents.  -->
<!ENTITY MakeBuilder "<function>Make</function>">



<!--

  Terms.  Define both singular and plural forms in various
  case-sensitive combinations for use in titles, in-line, etc.

-->

<!ENTITY buildfunc "<literal>builder function</literal>">
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
<!ENTITY Generator "<literal>Generator</literal>">
<!ENTITY generator "<literal>generator</literal>">

<!ENTITY Nodes "<literal>Nodes</literal>">

<!ENTITY signature "<literal>signature</literal>">
<!ENTITY buildsignature "<literal>build signature</literal>">

<!ENTITY true "<literal>true</literal>">
<!ENTITY false "<literal>false</literal>">

<!ENTITY typedef "<literal>typedef</literal>">

<!--

  File and program names used in examples.

-->

<!ENTITY bar "<application>bar</application>">
<!ENTITY common1_c "<filename>common1.c</filename>">
<!ENTITY common2_c "<filename>common2.c</filename>">
<!ENTITY custom_py "<filename>custom.py</filename>">
<!ENTITY goodbye "<application>goodbye</application>">
<!ENTITY goodbye_o "<filename>goodbye.o</filename>">
<!ENTITY goodbye_obj "<filename>goodbye.obj</filename>">
<!ENTITY file_dll "<filename>file.dll</filename>">
<!ENTITY file_in "<filename>file.in</filename>">
<!ENTITY file_lib "<filename>file.lib</filename>">
<!ENTITY file_o "<filename>file.o</filename>">
<!ENTITY file_obj "<filename>file.obj</filename>">
<!ENTITY file_out "<filename>file.out</filename>">
<!ENTITY foo "<application>foo</application>">
<!ENTITY foo_o "<filename>foo.o</filename>">
<!ENTITY foo_obj "<filename>foo.obj</filename>">
<!ENTITY hello "<application>hello</application>">
<!ENTITY hello_c "<filename>hello.c</filename>">
<!ENTITY hello_exe "<filename>hello.exe</filename>">
<!ENTITY hello_h "<filename>hello.h</filename>">
<!ENTITY hello_o "<filename>hello.o</filename>">
<!ENTITY hello_obj "<filename>hello.obj</filename>">
<!ENTITY libfile_a "<filename>libfile_a</filename>">
<!ENTITY libfile_so "<filename>libfile_so</filename>">
<!ENTITY new_hello "<application>new_hello</application>">
<!ENTITY new_hello_exe "<application>new_hello.exe</application>">
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
