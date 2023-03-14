# INF142Oblig1

# DISCLAIMER
- The usernames which are assigned are auto-generated, and only for that session (Like in Google docs);
It should not be a breach of the anonymity criteria. 

# How to run
1. Start the server, using: python RAPServer.py
2. Start one or multiple clients, using python RAPClient.py
  - If there are no Advisee's they are assigned that role
  - If there are Advisees the role selection is random, so one can end
  up with multiple Advisors, but a single advisee.
3. When a client is started, the terminal should give insctructions for the use of the application.

# Libaries
* _thread
  * For concurrently controlling the clients in the server
* socket
  * For sending and reveiving messages between client and server
* random
  * Assign random roles
* threading
  * Semaphores to protect critical sections in the server
  
# Known bugs
* If a client disconnects in the middle of the session a bug appears because the advisor or advisee doest not send a message. This may lead to other clients not receiving messages they should have received.
