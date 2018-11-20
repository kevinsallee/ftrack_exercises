# Ftrack Exercises

- Exercise 1: Register two locations, and automatically transfer from
locationA to locationB, and notify the user about the transfer
    - folder: [copy_from_a_to_b](copy_from_a_to_b)
- Exercise 2: Enforce description when task or asset version is approved.
    - folder: [enforce_description](enforce_description)
- Exercise 3: Copy asset build between projects
    - folder: [copy_asset_build](copy_asset_build)


### Remarks

- I treated exercises as separate entities. They could have had common
code, but I considered they should be independent.
- I preferred tackling the 3 exercises than to write unittests. I followed
this approach because when you have tight deadlines, it's generally the
approach chosen in this industry. I consider my test incomplete because
of complete lack of coverage. I think with 1 more day, I could have
finished it entirely.
- I lost a bit of time understanding key concepts, and quite a lot trying
to install ftrack_connect, and that put me behind schedule.
- I encountered some issues in each exercise, I listed them in the individual
READMEs.
- I kept my features in separate branches, my commits logical and did
PRs I validated myself for each change (except adding READMEs etc)