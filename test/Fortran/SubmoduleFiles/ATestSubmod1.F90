
SUBMODULE (TestMod) TestSubmod

    USE,INTRINSIC :: iso_fortran_env

    IMPLICIT NONE

    REAL(REAL64),SAVE :: localvar=0.0

CONTAINS

MODULE SUBROUTINE sub1 (arg)
    INTEGER(INT32),INTENT(IN) :: arg
    localvar=REAL(arg,REAL64)
END SUBROUTINE sub1

MODULE PROCEDURE func2
    func2 = arg + localvar
END PROCEDURE func2

MODULE PROCEDURE sub47
    arg="111"//TRIM(arg)//"111"
END PROCEDURE sub47

END SUBMODULE TestSubmod


