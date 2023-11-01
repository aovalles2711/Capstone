# Capstone-1

This capstone project will be purposed as a exercise programming system. It will allow the user to create workouts based on the category of muscle groups, corresponding with the days of the week. Within the muscle groups will be specified exercises to target those areas.

For the purpose of utilizing the Crow's Foot Notation we will catagorize the schema as such:

a. One muscle group has many exercises.
b. One set has many repetitions.
c. One exercise has many sets.
d. One week has many days.

The muscle groups category will have a "primary key" as the weeks category will contain a "foreign key." As mentioned in the list above, all categories will have many-to-many relationships due to the corresonding nature. Tables that will relate will be the exercise and set tables.
