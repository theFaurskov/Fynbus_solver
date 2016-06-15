This is an algorithm solver, with a generator, that takes number of "routes"" and number of "bids per entrepreneur" as input.
The program works by first creating a data set with "generator.py".
This data set gets named as earlier versions, with the change that it doesn't describe the number of entrepreneurs but the number of "bids per entrepreneur".

Example: "input-010-005-6300.txt"

First number: number of routes
Second number: number of bids per entrepreneur
Third number: Unique number based on time

When this has been done, the file "fynbus_to_kombee.py" has to be run, with the data set's name as input.
Its output will be the input name appended with ".modified"

Example: 
Input:		"generator.py -i input-010-005-6300.txt"
Output: 	"input-010-005-6300.txt.modified"

This will create a modified version of the data set, which can be loaded into "solution.py"
"solution.py" also takes the data set's name as input, and ".modified" must not be added to the input, since it does this itself.

Example:
Input:		"solution.py -i input-010-005-6300.txt"
Output: 	"input-010-005-6300.txt.out"
