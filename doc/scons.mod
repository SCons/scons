<!--

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
<!ENTITY Cons "<application>Cons</application>">
<!ENTITY gcc "<application>gcc</application>">
<!ENTITY Jam "<application>Jam</application>">
<!ENTITY Make "<application>Make</application>">
<!ENTITY Makepp "<application>Make++</application>">
<!ENTITY Python "<application>Python</application>">
<!ENTITY ranlib "<application>ranlib</application>">
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

<!ENTITY implicit-cache "<literal>--implicit-cache</literal>">
<!ENTITY implicit-deps-changed "<literal>--implicit-deps-changed</literal>">
<!ENTITY implicit-deps-unchanged "<literal>--implicit-deps-unchanged</literal>">

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

<!ENTITY Alias "<function>Alias</function>">
<!ENTITY Aliases "<function>Aliases</function>">
<!ENTITY Append "<function>Append</function>">
<!ENTITY Build "<function>Build</function>">
<!ENTITY CacheDir "<function>CacheDir</function>">
<!ENTITY Clean "<function>Clean</function>">
<!ENTITY Clone "<function>Clone</function>">
<!ENTITY Command "<function>Command</function>">
<!ENTITY Copy "<function>Copy</function>">
<!ENTITY Default "<function>Default</function>">
<!ENTITY DefaultRules "<function>DefaultRules</function>">
<!ENTITY Depends "<function>Depends</function>">
<!ENTITY Environment "<function>Environment</function>">
<!ENTITY Export "<function>Export</function>">
<!ENTITY Help "<function>Help</function>">
<!ENTITY Ignore "<function>Ignore</function>">
<!ENTITY Install "<function>Install</function>">
<!ENTITY InstallAs "<function>InstallAs</function>">
<!ENTITY Link "<function>Link</function>">
<!ENTITY Local "<function>Local</function>">
<!ENTITY Module "<function>Module</function>">
<!ENTITY Objects "<function>Objects</function>">
<!ENTITY Precious "<function>Precious</function>">
<!ENTITY Prepend "<function>Prepend</function>">
<!ENTITY Replace "<function>Replace</function>">
<!ENTITY Repository "<function>Repository</function>">
<!ENTITY RuleSet "<function>RuleSet</function>">
<!ENTITY Salt "<function>Salt</function>">
<!ENTITY SetBuildSignatureType "<function>SetBuildSignatureType</function>">
<!ENTITY SetContentSignatureType "<function>SetContentSignatureType</function>">
<!ENTITY SourceSignature "<function>SourceSignature</function>">
<!ENTITY SourceSignatures "<function>SourceSignatures</function>">
<!ENTITY Split "<function>Split</function>">
<!ENTITY TargetSignatures "<function>TargetSignatures</function>">
<!ENTITY Task "<function>Task</function>">

<!ENTITY str "<function>str</function>">
<!ENTITY zipfile "<function>zipfile</function>">

<!-- Obsolete, but referenced in old documents.  -->
<!ENTITY Cache "<function>Cache</function>">



<!--

  Construction variables.

-->

<!ENTITY BUILDERMAP "<varname>BUILDERMAP</varname>">
<!ENTITY BUILDERS "<varname>BUILDERS</varname>">
<!ENTITY SCANNERMAP "<varname>SCANNERMAP</varname>">
<!ENTITY SCANNERS "<varname>SCANNERS</varname>">
<!ENTITY TARFLAGS "<varname>TARFLAGS</varname>">
<!ENTITY TARSUFFIX "<varname>TARSUFFIX</varname>">



<!--

  Environment variables.

-->

<!ENTITY CC "<varname>CC</varname>">
<!ENTITY CCFLAGS "<varname>CCFLAGS</varname>">
<!ENTITY LIBPATH "<varname>LIBPATH</varname>">
<!ENTITY LIBS "<varname>LIBS</varname>">
<!ENTITY PYTHONPATH "<varname>PYTHONPATH</varname>">
<!ENTITY SCONSFLAGS "<varname>SCONSFLAGS</varname>">



<!--

  Function and method arguments.

-->

<!ENTITY build_dir "<varname>build_dir</varname>">
<!ENTITY exports "<varname>exports</varname>">
<!ENTITY source "<varname>source</varname>">
<!ENTITY target "<varname>target</varname>">



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

<!ENTITY signature "<literal>signature</literal>">
<!ENTITY buildsignature "<literal>build signature</literal>">

<!--

  File and program names used in examples.

-->

<!ENTITY common1_c "<application>common1.c</application>">
<!ENTITY common2_c "<application>common2.c</application>">
<!ENTITY goodbye "<application>goodbye</application>">
<!ENTITY hello "<application>hello</application>">
<!ENTITY hello_c "<filename>hello.c</filename>">
<!ENTITY hello_exe "<filename>hello.exe</filename>">
<!ENTITY hello_h "<filename>hello.h</filename>">
<!ENTITY hello_o "<filename>hello.o</filename>">
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

<!ENTITY scons-announce "<literal>scons-announce@lists.sourceforge.net</literal>">
<!ENTITY scons-devel "<literal>scons-devel@lists.sourceforge.net</literal>">
<!ENTITY scons-users "<literal>scons-users@lists.sourceforge.net</literal>">
