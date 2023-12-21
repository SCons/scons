
program main
    use module0
    use module1
    use module2
    use util_module
    implicit none
    write(*,*) 'Main program using modules!'
    call module0_subroutine()
    call module1_subroutine()
    call module2_subroutine()
    call util_subroutine()
end program main
