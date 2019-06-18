%{
#include<stdio.h>

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
main()
{
 return(yyparse());
}

yyerror(s)
char *s;
{
  fprintf(stderr, "%s\n",s);
  return(0);
}

yywrap()
{
  return(1);
}