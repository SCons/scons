program test_submodules

  use test_1
  use test_2

  type(test_type_1) :: var1
  type(test_type_2) :: var2

  call var1%set_n(42)
  call var2%set_m(21)

  print*,'var1%n = ', var1%get_n()
  print*,'var2%m = ', var2%get_m()

  call var1%increment_n()
  call var2%increment_m()

  print*,'var1%n = ', var1%get_n()
  print*,'var2%m = ', var2%get_m()

  call var1%decrement_n()
  call var2%decrement_m()

  print*,'var1%n = ', var1%get_n()
  print*,'var2%m = ', var2%get_m()

end program test_submodules
