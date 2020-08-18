
MODULE TestMod

    USE,INTRINSIC :: iso_fortran_env

    INTERFACE
        MODULE SUBROUTINE sub1 (arg)
            INTEGER(INT32),INTENT(IN) :: arg
        END SUBROUTINE sub1

        MODULE FUNCTION func2 (arg)
            REAL(REAL64) :: func2
            REAL(REAL64),INTENT(IN) :: arg
        END FUNCTION func2

        MODULE SUBROUTINE sub47 (arg)
            CHARACTER(LEN=*),INTENT(INOUT) :: arg
        END SUBROUTINE sub47
    END INTERFACE

END MODULE TestMod


