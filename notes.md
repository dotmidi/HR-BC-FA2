* [X] Figuring out how to assign 2 different nodes without changing variables
* [X] Not allow 1 user to be connected from 2 different nodes
* [X] Ending litening gracefully
* [X] Sending

  * [X] Simple messages
  * [X] Items (Blocks, Tx, etc.)
    * [X] Newly created transactions
      * [X] Validating on the receiving side
    * [X] Newly mined blocks
      * [X] Validating on the receiving side
* [X] Receiving

  * [X] Simple messages
  * [X] Items (Blocks,Tx, etc.)
    * [X] Newly created transactions
    * [X] Newly mined blocks
* [X] Sync on-demand

  * [X] When both nodes are occupied, they sync with each other. Pool and ledger files are sent to each other, they both check validity and come to a consensus.
* [X] ISSUE: Who sends the newly registered user' transactions over the network?

  * [X] solution: the perosn who logs into the node with the newly registered user' transactions in the pool first
* [X] FIX THE ERROR FROM THE PREVIOUS SHOWCASE, THE BALANCE SHOULD BE LOWER WHEN MAKING A TRANSACTION IMMEDIATLEY, NOT BE SHOWN AS USABLE
* [X] Change all of the 3/3 validations required to 1 (because of just 2 nodes being utilized for the demo)
* [X] double check sent tx-txblock-ledger-pool that they are saved on sending and saved on receiving
* [X] the json for connected_users isn't shared, look for other solution
* [X] clean up simulatenous mining print
* [X] sync user databases

  * [X] Works, but remove the known_to_all, just yeet all of them at once to the other side and use the try catch exception to only insert new ones




* [ ] Test further
  * [ ] Sign up 3 users in node1, 2 in node2
  * [ ] login on both nodes, the registered users on both are synced
  * [ ] mine block 0 on node1 with node2 connected
  * [ ] log out node2 and log back in to validate mined block by node1
  * [ ] create -> edit -> delete a transaction in node1
  * [ ] log off node2
  * [ ] create 4 transactions in node1 to be able to mine
  * [ ] mine block 1 on node1 with node2 disconnected
  * [ ] log node2 back in, sync
