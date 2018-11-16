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
But the last submit, where everything is updated, doesn't refresh the web
UI.
- Closing the dialog with the "X" will just quit and not enforce to have
a description. One solution would be to, upon receiving tasks/versions
which don't have a description, to reset the status to its previous value,
and actually set it to approved only if the description was indeed filled.
But I feel that would be confusing. The other solution would be to actually
build a widget (instead of using a form), that way you can enforce anything
you want.


