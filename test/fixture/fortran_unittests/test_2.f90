module test_2

  type test_type_2
    integer :: m
    contains
      procedure :: set_m
      procedure :: get_m
      procedure :: increment_m
      procedure :: decrement_m
  end type test_type_2


interface

  module subroutine set_m ( this, m )
    class(test_type_2), intent(inout) :: this
    integer, intent(in) :: m
  end subroutine

  module function get_m ( this )
    class(test_type_2), intent(in) :: this
    integer :: get_m
  end function get_m

  module pure subroutine increment_m ( this )
    class(test_type_2), intent(inout) :: this
  end subroutine increment_m

  module elemental subroutine decrement_m ( this )
    class(test_type_2), intent(inout) :: this
  end subroutine decrement_m

end interface

end module test_2


submodule(test_2) test_2_impl

contains

  module procedure set_m

    implicit none

    this%m = m
  end procedure set_m

  module procedure get_m

    implicit none

    get_m = this%m
  end procedure get_m

  module procedure increment_m

    implicit none

    this%m = this%m+1
  end procedure increment_m

  module procedure decrement_m

    implicit none

    this%m = this%m-1
  end procedure decrement_m

end submodule test_2_impl
