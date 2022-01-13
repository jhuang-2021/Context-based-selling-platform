# Cloud-base Contest-selling platform

This project implements an API to support both the backend and the frontend
operations for selling/buying products or services on a contest basis.

The software is supposed to run on a server. However, it can also be run 
on the application-engineer's local server under the usual IP address:
127.0.0.1, port 5000

The backend is implemented using Python 3.7 and flask. The frontend
is served using HTML5 and CSS, with small amount of javascript.

The SQLAlchemy package is used as the interface for database, while 
the application of the project can be run using any database server,
such as SQL, NoSQL, PostgreSQL, MongoDB, etc.The communication interface
between flask and the database server remains the same. This approach
provide an excellent extensibility for the applications.

The RESTful API approach is used for data security and easy-of-use. 


## The ideas behind this implementation

For a product or a service someone wants to sell or buy to use this platform, 
the process involves a few steps:

1. User Registration: one needs to register on the platform and create a user account
2. Buyer Registratio: on top of the User Registration, to buy a product or service, 
      you need to register as a buyer
3. Seller Registration: apart from user registration, if you want to sell 
   a product or service, you need to register as a seller
4. The status of a seller needs to be verified by the system administrator
   of this platform. This resembles the validation process of any potential
   seller
5. Any user can register as both a seller and a buyer
6. The sell/buy process starts with a buyer submit a 'competition', which 
   defines his/her needs in a JSON string. 
   The main elements of a 'competition' itm consist of:
   a) Opening time for the competition 
   b) The close time for the competition
   c) Minimun capacity: this is an abstraction of some kind of requirement,
      which can be replaced with more specific description of requirement
   d) Currency type for the buy/sell process
   A buyer can submit any number of competitions as he/she wishes.
7. Sellers than submit bids against the advertised competition. A bid mush satisfy 
   the minimum requirement as described in the comptition, this includes:
   a) The bid must be submitted within the time frame of the opening time 
       and close time 
   b) The seller's status much be verified
   c) The offered capacity must be no less than the minimun capacity
      as stated in the competition.
   A seller can submit any number of bids against different competitions
   
## Functionality of the platform

1. User account: registration, login, logout
2. Admin operations: an admin must also be registered as an user first.
   a) Get admin status: a user can be upgraded as an admin by matching the password 
      against the system stored password
   b) Update server: this will load the json files stored in the server,
      and use those files to update the database. Any item which
      are already in the database will not be re-stored to elliminate 
      duplication of data items. 
   c) Verify seller status
   d) Accept bids
3. Sell and buy operations
   a) register as a buyer
   b) register as a seller
   c) Put a competition
   d) Search all competitions which has at least one successful bid
   e) List all competitions for some specific information
   
## About the code testing

In the flask interface with the frontend users. error trap mechanism 
is throughtly implemented, so that when an error occurs at the input
string, it is properly captured and handled. This approach has the advantage 
of making the implementation neater, easier to extend. As a result,
we do not need to develop specific test cases for the relevant features.

## Dependancy of software packages

The application is assumed to run on Linux. Not testd for
windows or any other platform.

It also  assumes that one has Python 3.x and pip installed in their
system. The requirements.txt file describes the extra packages which are
needed to run the code. To implement the requirement, do:



pip install -r requirements.txt 

Note: some system name the pipn for Python3 as pip3. In that case, you ned to do:

pip3 install -r requirements.txt 

To start up the application, do 

./run.sh

This will start up the flask server

In the web browser, go to:

http://0.0.0.0:5000/

The user interface will be seen.




