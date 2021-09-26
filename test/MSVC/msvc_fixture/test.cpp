#include "StdAfx.h"
#include "resource.h"

int main(void) 
{ 
    char test[1024];
    LoadString(GetModuleHandle(NULL), IDS_TEST, test, sizeof(test));
    printf("%d %s\n", IDS_TEST, test);
    return 0;
}