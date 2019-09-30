/*

******************************************************************************************
                         NOTES ON HOW TO USE AND MODIFY THIS FILE
******************************************************************************************

This file is used at the beginning of your project to create the SQLite database in which
all recorded experiment data is stored.

By default there are only two tables that KLibs writes data to: the 'participants' table,
which stores demograpic and runtime information, and the 'trials' table, which is where
the data recorded at the end of each trial is logged. You can also create your own tables
in the database to record data for things that might happen more than once a trial
(e.g eye movements) or only once a session (e.g. a questionnaire or quiz), or to log data
for recycled trials that otherwise wouldn't get written to the 'trials' table.


As your project develops, you may change the number of columns, add other tables, or
change the names/datatypes of columns that already exist.

To do this, modify this document as needed, then rebuild the project database by running:

  klibs db-rebuild

while within the root of your project folder.

But be warned: THIS WILL DELETE ALL YOUR CURRENT DATA. The database will be completely 
destroyed and rebuilt. If you wish to keep the data you currently have, run:

  klibs export

while within the root of your project folder. This will export all participant and trial
data in the database to text files found in NP_IOR/ExpAssets/Data.


Note that you *really* do not need to be concerned about datatypes when adding columns;
in the end, everything will be a string when the data is exported. The *only* reason you
would use a datatype other than 'text' would be to ensure that the program will throw an
error if, for example, it tries to assign a string to a column you know is always going
to be an integer.

*/

CREATE TABLE participants (
    id integer primary key autoincrement not null,
    userhash text not null,
    gender text not null,
    age integer not null, 
    handedness text not null,
    created text not null
);

CREATE TABLE trials (
    id integer primary key autoincrement not null,
    participant_id integer not null references participants(id),
    block_num integer not null,
    trial_num integer not null,
    practicing text not null,
    far_near text not null,
    trial_type text not null,
    prime_rt text not null,
    probe_rt text not null,
    prime_correct text not null,
    probe_correct text not null,
    t_prime_to_t_probe text not null,
    t_prime_to_d_probe text not null,
    d_prime_to_t_probe text not null,
    d_prime_to_d_probe text not null,
    prime_choice text not null,
    probe_choice text not null,
    prime_response text not null,
    probe_response text not null,
    t_prime_loc text not null,
    d_prime_loc text not null,
    t_probe_loc text not null,
    d_probe_loc text not null
);
