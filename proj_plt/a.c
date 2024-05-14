extern int foo;

int func() {
  return foo;
}

int func1() {
  foo = 300;
  return foo;
}
