
module module0
    use module1
    use module2
    implicit none
contains
    subroutine module0_subroutine()
        write(*,*) 'This is module0 subroutine.'
    end subroutine module0_subroutine
end module module0
