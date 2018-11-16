# Location A and Location B exercise

- Create two locations, location.a and location.b, and register them in
ftrack connect
- Use ftrack connect to publish. It will publish to the first registered
location, location.a.
- Use copy_to_location_b event to copy the component from location.a to location.b

### Problems encountered

- I could not install ftrack_connect on my Mac. I had Qt5 installed,
so that was causing some issues, I installed Qt4 using https://github.com/cartr/homebrew-qt4,
that allowed me to install PySide for example, but when trying to install
ftrack_connect I still get an error:
`
Could not find a version that satisfies the requirement qtext (from ftrack-connect==1.1.6) (from versions: )
No matching distribution found for qtext (from ftrack-connect==1.1.6)`
- The way I solved this is by putting my code where ftrack connect is
expecting it. Not ideal.
- I could not find a proper way of defining the persistence of the message
sent back to the web UI. Since I was publishing from ftrack-connect, by
the time I got back to the UI, the message was gone. I hacked it by using
a form with a label. I could also use a simple custom widget. Or maybe the
best way is to actually add a Note somewhere so it ends up in the Inbox?