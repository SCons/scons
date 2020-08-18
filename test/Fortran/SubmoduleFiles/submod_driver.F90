
PROGRAM submod_driver

    USE,INTRINSIC :: iso_fortran_env

    USE TestMod

    IMPLICIT NONE

    REAL(REAL64) :: RetvalReal
    CHARACTER(LEN=1024) :: RetvalString


    !======================================================================
    ! proceed
    !======================================================================

    CALL sub1(123)
    RetvalReal=func2(REAL(456,REAL64))
    WRITE(UNIT=*,FMT='(a,es22.15)') "result of ""sub1(123)"" and ""func2(456))"": ",RetvalReal
    WRITE(UNIT=RetvalString,FMT='(a)') "BlahBlepBloop"
    CALL sub47(RetvalString)
    WRITE(UNIT=*,FMT='(a,a,a)') "result of sub47(""BlahBlepBloop""): """,TRIM(RetvalString),""""

    WRITE(UNIT=*,FMT='(a)') ""

END PROGRAM submod_driver


