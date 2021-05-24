%{
#include<stdio.h>

int yyerror(char *s);
int yylex();

int regs[26];
int base;

%}

%start digit

%union { int a; }


%token DIGIT LETTER

%left '|'
%left '&'
%left '+' '-'
%left '*' '/' '%'
%left UMINUS  /*supplies precedence for unary minus */

%%                   /* beginning of rules section */

digit: DIGIT;


%%
int
main()
{
 return(yyparse());
}

int
yyerror(s)
char *s;
{
  fprintf(stderr, "%s\n",s);
  return(0);
}

int
yywrap()
{
  return(1);
}
