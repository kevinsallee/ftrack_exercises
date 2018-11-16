# Enforce Description on approval

- When a list of Tasks and/or AssetVersions are approved in the web UI,
but have no descriptions, a form will appear which will allow the user
to fill in missing descriptions.

- If the user leave some empty, a new form will appear until all approved
entities have a description.

### Problems encountered

- I could not find an "elegant" way of dealing with the form results other
than suscribing to `topic=ftrack.action.launch` with an `actionIdentifier`
set manually.
- I could not find a proper way of refreshing the web UI after all missing
descriptions are updated. When you don't update all of them, you will get
another form, and the ones you updated are indeed refreshed automagically.


