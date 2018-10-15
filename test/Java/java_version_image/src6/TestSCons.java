class test
{
    test()
    {
        super();
        new inner();
    }

    static class inner
    {
        private inner() {}
    }
}
