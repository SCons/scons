
SUBMODULE (TestMod) TestSubmodParent

    USE,INTRINSIC :: iso_fortran_env

    IMPLICIT NONE

    INTERFACE
        MODULE SUBROUTINE sub1child (arg)
            INTEGER(INT32),INTENT(IN) :: arg
        END SUBROUTINE sub1child

        MODULE FUNCTION func2child (arg)
            REAL(REAL64) :: func2child
            REAL(REAL64),INTENT(IN) :: arg
        END FUNCTION func2child

        MODULE SUBROUTINE sub47child (arg)
            CHARACTER(LEN=*),INTENT(INOUT) :: arg
        END SUBROUTINE sub47child
    END INTERFACE

CONTAINS

MODULE SUBROUTINE sub1 (arg)
    INTEGER(INT32),INTENT(IN) :: arg
    CALL sub1child(arg)
END SUBROUTINE sub1

MODULE PROCEDURE func2
    func2 = func2child(arg)
END PROCEDURE func2

MODULE PROCEDURE sub47
    CALL sub47child(arg)
END PROCEDURE sub47

END SUBMODULE TestSubmodParent


