from klibs.KLIndependentVariable import IndependentVariableSet

NP_IOR_ind_vars = IndependentVariableSet()

# Prime items are always presented at the far points of the array,
# Probe items can either appear at the far points, or near points (but not both), respective to fixation
NP_IOR_ind_vars.add_variable('far_or_near', str, ['far', 'near'])
NP_IOR_ind_vars.add_variable('prime_target', int, [1, 2, 3, 4])
NP_IOR_ind_vars.add_variable('prime_distractor', int, [1, 2, 3, 4])
NP_IOR_ind_vars.add_variable('probe_target', int, [1, 2, 3, 4, 5, 6, 7, 8])
NP_IOR_ind_vars.add_variable('probe_distractor', int, [1, 2, 3, 4, 5, 6, 7, 8])


"""
*** SAMPLE CONFIGURATION - REMOVE AFTER FINISHING REAL CONFIG ***

First we create an IndependentVariableSet object that will group together all the independent variables the experiment
will use, like so:

>> NP_IOR_ind_vars = IndependentVariableSet()

Then we create empty variables within this set. At this point we're not providing any values, just a name and a data
type that will tell klibs that this variable exists and what pythonic data type it should expect that variable's values
to hold. In this example we create four variables, one for each type.

>> NP_IOR_ind_vars.add_variable("color", str)
>> NP_IOR_ind_vars.add_variable("size", float)
>> NP_IOR_ind_vars.add_variable("active", bool)
>> NP_IOR_ind_vars.add_variable("count", int)

Finally, we add values to each variable. This can be done one at a time, as in the colors example below:

>> NP_IOR_ind_vars['color'].add_value("blue")
>> NP_IOR_ind_vars['color'].add_value("blue")
>> NP_IOR_ind_vars['color'].add_value("blue")

Or altogether in a comma-separated set, as in the 'count' example:

>> NP_IOR_ind_vars['count'].add_values(1,2,3,4,5)

Finally, values can have a distribution attached to them in case some values should feature more or less frequently, with
respect to one and other, in the experiment. For example, if we wanted to have the 'size' variable be either 1.0 or 2.0
occur more frequently than 5.0, we could add these values as such:

>> NP_IOR_ind_vars['size'].add_value(1.0, 2)
>> NP_IOR_ind_vars['size'].add_value(2.0, 2)
>> NP_IOR_ind_vars['size'].add_value(5.0)

Note that the there is no distribution value included for the third option. By default, every value has a distribution of
1. You only need to set the distribution when it is larger than 1.

Now, for every 5 trials that are generated from this IndependentVariableSet, only one of them will have 5.0 as the value
of the 'size' independent variable.

Adding distributions to values is also possible when adding values as a set by creating a tuple for each value, like so:

>> NP_IOR_ind_vars['active'].add_values((True, 5), False)

which is equivalent to:

>> NP_IOR_ind_vars['active'].add_value(True, 5)
>> NP_IOR_ind_vars['active'].add_value(False)

As a final note, you may wish to selectively exclude certain values or even entire independent variables during development
and testing. By default, all IndependentVariables and their values are enabled, but you can disable them by toggling their
enabled parameter:

>> NP_IOR_ind_vars['size'].enabled = False

Now there will be no contribution for the 'size' independent variable during trial generation. Note that this independent
variable will still exist at runtime (ie. the Experiment class will be able to reference 'self.size' but it's value will
be None and will not change between trials.

Similarly, individual values can also be disabled.

>> NP_IOR_ind_vars['size'][1.0].enabled = False

"""