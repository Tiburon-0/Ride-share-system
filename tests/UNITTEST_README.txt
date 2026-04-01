===========Design Decisions==========

unittests run via menu option 4 in main.py

menu in main.py is wrapped in if __name__ == '__main__': so test files can import from it without launching the menu

tests use small hand-built graphs instead of the random BA graph 
**The correct answer is always known in advance

setUp() creates fresh objects before each test so tests never affect each other

make_driver() and make_rider() helper functions are implemented in test_matching.py to reduce repeated setup code

==========Known Limitations============

Full fare testing requires a distance value that is normally set by the production graph
*Solution: It is set manually in the integration test
