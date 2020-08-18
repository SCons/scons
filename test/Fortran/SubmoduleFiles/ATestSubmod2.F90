
SUBMODULE (TestMod:TestSubmodParent) TestSubmodChild

    USE,INTRINSIC :: iso_fortran_env

    IMPLICIT NONE

    REAL(REAL64),SAVE :: localvar=0.0

CONTAINS

MODULE SUBROUTINE sub1child (arg)
    INTEGER(INT32),INTENT(IN) :: arg
    localvar=REAL(arg,REAL64)
END SUBROUTINE sub1child

MODULE PROCEDURE func2child
    func2child = (arg + localvar)*(arg + localvar)
END PROCEDURE func2child

MODULE PROCEDURE sub47child
    arg="222"//TRIM(arg)//"222"
END PROCEDURE sub47child

END SUBMODULE TestSubmodChild


