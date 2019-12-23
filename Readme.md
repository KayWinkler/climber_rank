# Evaluate climbers rank

This project uses the website https://www.digitalrock.de/ which provides a
set of climbing competition results. From these results it allows to extrakt
a set of competitors and list their direct competitions and their rank in
comparison.

# usage

## 0. open a terminal

## 1. change to the location of the installation

Command:

    cd workspace/climber_rank

## 2. activate your runtime environment:

Command:

    source env/bin/activate

## 3. run the program

### 3a. Fetch the competition data

in the file 'gather.py' lok for the line 'fetch_competition' and verify
that the value is 'True'

    fetch_competitions = True

If you dont need the initial download anymore set the value to 'False'

After the command:

    ./gather.py

the available competitions are stored in the subdirectory 'competitions'.

### 3b. Create an index about all participants:

in the file 'gather.py' search for the 'build_participants_index' and verify that the value is set to 'True'.

    build_participants_index = True

If not needed anymore, the value should be set to 'False'.

After the command:

    ./gather.py

the file 'participants.json' has been created in the 'competitions' directory. It contains the list of all users and
their participation in a competition with the discipline and resulting rank

### 3c. Create the participant tabels:

in the file 'gather.py' verify that the value for 'build_participants_table' is set to 'True'

    build_participants_table = True

if not needed anymore, set it to the value 'False'.

In addition put in the file 'gather.py' the list of users, which should be evaluated.

        . . .
        users = []

        users.append("Anna-Lena:Wolf")
        users.append("Emilia:Merz")
        users.append("Julanda:Peter")

Be aware, that a ':' should be added between the firstname and the lastname.

After the command:

    ./gather.py

the following results were create in the subdirectory 'competitions'

* Bouldern.csv
* Lead.csv
* Speed.csv
* Combined.csv

These files represent the input data for the matrix ranking evaluation 'rank.py'.
