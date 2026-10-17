import code
from chatPGTips import chatPGTips

# Print some brief instructions to console
print("Starting interactive console with chatPGTips...\n"+
      "\n"+
      "Try e.g.:\n"+
      ">>> monkey.ask('What is this all about?')\n"+
      ">>> monkey.who()\n"+
      ">>> monkey.why()\n"+
      ">>> monkey.what()\n"+
      "etc...")

# Initiate class
monkey = chatPGTips()

# Start interactive session in console
code.interact(local={chatPGTips, monkey})

'''
Note: local defines what the user can access
it can be simple/tempting to pass the user everything, e.g. local=locals() or local=globals()
(and in fact this can be a useful debug tool)
However...
This means the user can do EVERYTHING the code can do!!
This includes e.g. editing the page if you have pyscript modules imported!!
'''
