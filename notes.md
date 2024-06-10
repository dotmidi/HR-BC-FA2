* [X] Figuring out how to assign 2 different nodes without changing variables
* [X] Not allow 1 user to be connected from 2 different nodes
* [X] Ending litening gracefully
* [X] Sending
  * [X] Simple messages
  * [X] Items (Blocks, Tx, etc.)
    * [X] Newly created transactions
      * [X] Validating on the receiving side
    * [ ] Newly mined blocks
      * [ ] Validating on the receiving side
* [X] Receiving
  * [X] Simple messages
  * [ ] Items (Blocks,Tx, etc.)
    * [ ] Newly created transactions
    * [ ] Newly mined blocks
* [ ] Sync on-demand
  * [ ] When both nodes are occupied, they sync with each other. Pool and ledger files are sent to each other, they both check validity and come to a consensus.
* [ ] ISSUE: Who sends the newly registered user' transactions over the network?
* [X] FIX THE ERROR FROM THE PREVIOUS SHOWCASE, THE BALANCE SHOULD BE LOWER WHEN MAKING A TRANSACTION IMMEDIATLEY, NOT BE SHOWN AS USABLE
