* [X] allow users to select transactions to mine from the pool (?) (maybe better to just let the system automatically determine which has the highest fee and put those on top)
* [X] maybe make the block validation run on login instead of blockchain explore (didnt go for it in the end)
* [X] split the hashing of the data files into seperate hashes so the system can print which data file has been tampered with
* [X] make the mining even easier after 15s
  * [X] test
* [X] add extra info on some menu options
  * [X] make transaction: "Transactions with the highest fee's will have priority in the pool"
  * [X] etc.
* [X] notification system
  * [X] whenever
    * [X] a user's transaction is mined
    * [X] a miner's block got validated
* [X] automatic login actions
  * [X] check tx pool and remove invalid transactions
    * [X] remove functionality from check_pool
  * [X] entire blockchain check
    * [X] validate
    * [X] if 3 flags => add reward tx to pool
    * [X] if 3 invalidFlags => remove block
    * [X] remove functionality from user_check_ledger
