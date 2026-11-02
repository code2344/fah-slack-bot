This is just my logic ideas (pseudocode)

if argument is empty:
    respond("you need the argument")
else:
    if argument can be converted to a number:
      db.link_user(slack id, argument)
    else:
      argument was invalid
