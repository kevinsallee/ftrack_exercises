# Copy asset build action

- When a user selects a single Asset Build, allows to copy to another project

- an enumerator will allow the user to choose a destination project

- if no destination project is selected, the form reopens

- if the AssetBuild object type does not exist in the resulting project,
the action fails.

- if an AssetBuild with the same name already exists, it will rename it
`$ORIGINAL_NAME (i)`

### Problems encountered

- I'd like to filter out projects which don't have AssetBuilds in their
project schema. I tried to find a way but could not. Found a post that
pointed that this is not possible: https://forum.ftrack.com/topic/1328-query-project-schema-objects/.
I could have gone for an approach of trying to create an asset build and
filter out the projects that can't create it. I preferred not doing that,
for performance purposes. If you try to copy to a project that does not
have asset builds, it will just fail and send a fail message.

- The AssetBuild, when discovering actions, has a type `task`, not `assetbuild`
I found that strange but there might be a reason for that.

- The instructions did not say if a deep copy was needed (tasks, versions,
components and all their files in different locations). I would have liked
to do that, but I did not have time. Furthermore, I felt that some instructions
were missing if I wanted to copy it "fully": what fields should be kept for each
object type? Do we reset statuses, not put assignees, etc?
So instead it's just linking to the "original" asset build
