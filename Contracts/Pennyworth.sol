pragma solidity ^0.6.0;
// Code inspired by https://thisartworkisalwaysonsale.com/

import "./interfaces/IERC721.sol";
import "./utils/SafeMath.sol";

contract PennyWorth{
    using SafeMath for uint256;

    uint256 public price; //in Wei
    uint256 public tokenID; // ID of the Token that is generated via the setup() function
    IERC721 public art; // ERC721 NFT.

    uint256 public totalCollected; // all patronage ever collected

    /* In the event that a foreclosure happens AFTER it should have been foreclosed already,
    this variable is backdated to when it should've occurred. Thus: timeHeld is accurate to actual deposit. */
    uint256 public timeLastCollected; // timestamp when last collection occurred
    uint256 public deposit; // funds for paying patronage
    address payable public artist; // beneficiary
    uint256 public artistFund; // what artist has earned and can withdraw

    /*
    If for whatever reason the transfer fails when being sold,
    it's added to a pullFunds such that previous owner can withdraw it.
    */
    mapping (address => uint256) public pullFunds; // storage area in case a sale can't send the funds towards previous owner.

    uint256 public timeAcquired; // when it is newly bought/sold

    // percentage patronage rate. eg 5% or 100% 
    uint256 patronageNumerator; 

    // Logs if it has been sold once 
    bool before_first_sale;

    // init that logs if the contract has run before
    bool init;


    /* 
    _artist ->  Adress of Artist 
    _artwork -> Adress of Art 
    _tokenId -> ID of the token, must be identical with the TokenID of the Artwork
    _patronage -> patronage or dividend payed towards the artist (per annum) in % 
    */

    constructor(address payable _artist, address _artwork, uint256 _tokenId, uint256 _patronage) public {
        // Artwork has not been bought / sold
        before_first_sale = true;
        // this is kept here in case you want to use this in an upgradeable contract
        require(init == false, "PennyWorth already initialized.");
        // set Token-ID, has to be same token-ID that is used in the erc contract 
        tokenID = _tokenId;
        // variable % to be given to the beneficiary / artist
        patronageNumerator = _patronage.div(100);
        // get deployed artwork Contract 
        art = IERC721(_artwork);
        // Initialising ERC 721 Contract 
        art.setup();
        // set-up artist
        artist = _artist;

        //sets up initial parameters for foreclosure
        _forecloseIfNecessary();

        init = true;
    }


    event LogBuy(address indexed owner, uint256 indexed price);
    event LogPriceChange(uint256 indexed newPrice);
    event LogForeclosure(address indexed prevOwner);
    event LogCollection(uint256 indexed collected);

    // modifier to make sure the method is only used by the patron
    modifier onlyPatron() {
        require(msg.sender == art.ownerOf(tokenID), "Not patron");
        _;
    }

    // modifier that runs the patronage collection
    modifier collectPatronage() {
       _collectPatronage(); 
       _;
    }

    /* public view functions */
    /* used internally in external actions */

    // returns how much is owed from last collection to now.
    // price * zeit_diff * prozentsatz / 365 Tage 
    function patronageOwed() public view returns (uint256 patronageDue) {
        return price.mul(now.sub(timeLastCollected)).mul(patronageNumerator).div(365 days);
    }

    // returns how much time will it take until that amount of patronage is due -> time in seconds
    // _time => time difference in seconds 
    // REWORK 
    function patronageOwedRange(uint256 _time) public view returns (uint256 patronageDue) {
        return price.mul(_time).mul(patronageNumerator).div(365 days);
    }

    // returns how much seconds are in a year 
    function seconds_year() public view returns (uint256 seconds_per_year) {
        return 365 days;
    }

    // returns the current patronage
    function getPatronage() public view returns (uint256 numerator){
        return patronageNumerator;
    }

    // returns how much has been collected since last collection
    function currentCollected() public view returns (uint256 patronageDue) {
        if(timeLastCollected > timeAcquired) {
            return patronageOwedRange(timeLastCollected.sub(timeAcquired));
        } else { return 0; }
    }

    // returns wether or not the artwork is in in state before sale 
    function before_sale_state() public view returns (bool state) {
        return before_first_sale;
    }

    // returns how much patronage would be owned at the given timestamp 
    function patronageOwedWithTimestamp() public view returns (uint256 patronageDue, uint256 timestamp) {
        return (patronageOwed(), now);
    }

    /* 
    returns whether it is in foreclosed state or not
    depending on whether deposit covers patronage due
    useful helper function when price should be zero, but contract doesn't reflect it yet. 
    */
    function foreclosed() public view returns (bool) {
        uint256 collection = patronageOwed();
        if(collection >= deposit) {
            return true;
        } else {
            return false;
        }
    }

    // same function as above, basically
    function depositAbleToWithdraw() public view returns (uint256) {
        uint256 collection = patronageOwed();
        if(collection >= deposit) {
            return 0;
        } else {
            return deposit.sub(collection);
        }
    }

    /*
    now + deposit/patronage per second 
    now + depositAbleToWithdraw/(price*nume/denom/365).
    */
    // REWORK
    function foreclosureTime() public view returns (uint256) {
        // patronage per second
        uint256 pps = price.mul(patronageNumerator).div(365 days);
        uint256 daw = depositAbleToWithdraw();
        // Do we have patronage to withdraw?
        if(daw > 0) {
            return now + depositAbleToWithdraw().div(pps);
        } else if (pps > 0) {
            // it is still active, but in foreclosure state
            // it is NOW or was in the past
            uint256 collection = patronageOwed();
            return timeLastCollected.add(((now.sub(timeLastCollected)).mul(deposit).div(collection)));
        } else {
            // not active and actively foreclosed (price is zero)
            return timeLastCollected; // it has been foreclosed or in foreclosure.
        }
    }

    /*! actions */
    // determine patronage to pay
    function _collectPatronage() public {
        
        // Only calculate patronage if the artwork has not been sold and the artist is the owner
        if ((art.ownerOf(tokenID) != artist) && before_first_sale == false){
        
            if (price != 0) { // price > 0 == active owned state
                uint256 collection = patronageOwed();
                
                if (collection >= deposit) { // foreclosure happened in the past

                    // up to when was it actually paid for?
                    // TLC + (time_elapsed)*deposit/collection
                    timeLastCollected = timeLastCollected.add((now.sub(timeLastCollected)).mul(deposit).div(collection));
                    collection = deposit; // take what's left.
                } else { 
                    timeLastCollected = now; 
                } // normal collection

                deposit = deposit.sub(collection);
                totalCollected = totalCollected.add(collection);
                artistFund = artistFund.add(collection);
                emit LogCollection(collection);

                _forecloseIfNecessary();
            }
        }
    }


    // Allows an actor to buy the artwork through pennyworth at a specified price
    function buy(uint256 _newPrice, uint256 _currentPrice) public payable collectPatronage {
        /* 
            this is protection against a front-run attack.
            the person will only buy the artwork if it is what they agreed to.
            thus: someone can't buy it from under them and change the price, eating into their deposit.
        */

        // front-running protection
        require(price == _currentPrice, "Current Price incorrect");
        // can't be bought for nothing
        require(_newPrice > 0, "Price is zero");
        // message needs to cover more than the sales price, rest will go towards deposit
        require(msg.value > price, "Not enough"); // >, coz need to have at least something for deposit

        address currentOwner = art.ownerOf(tokenID);

        uint256 totalToPayBack = price.add(deposit);
        if(totalToPayBack > 0) { // this won't execute if PennyWorth owns it. price = 0. deposit = 0.
            // pay previous owner their price + deposit back.
            address payable payableCurrentOwner = address(uint160(currentOwner));
            bool transferSuccess = payableCurrentOwner.send(totalToPayBack);

            // if the send fails, keep the funds separate for the owner
            if(!transferSuccess) { pullFunds[currentOwner] = pullFunds[currentOwner].add(totalToPayBack); }
        }

        // artwork is being bought, thus it is not in the "before_first_sale" state.
        before_first_sale = false;

        // new purchase
        timeLastCollected = now;
        
        // deposit is the value that is being sent via message - price
        deposit = msg.value.sub(price);
        // transfering artwork to the buyer
        transferArtworkTo(currentOwner, msg.sender, _newPrice);
        emit LogBuy(msg.sender, _newPrice);
    }

    /* !Only Patron Actions */
    // deposit wei into the contract 
    function depositWei() public payable collectPatronage onlyPatron {
        deposit = deposit.add(msg.value);
    }

    // change the price of the artwork
    function changePrice(uint256 _newPrice) public collectPatronage onlyPatron {
        require(_newPrice > 0, 'Price is zero'); 
        price = _newPrice;
        emit LogPriceChange(price);
    }
    
    // withdraw entire deposit, collect patronage first, only to be accessed by patron
    function withdrawDeposit(uint256 _wei) public collectPatronage onlyPatron {
        _withdrawDeposit(_wei);
    }

    // allows the patron to "exit" the artwork
    function exit() public collectPatronage onlyPatron {
        _withdrawDeposit(deposit);
    }

    /* !Actions that don't affect state of the artwork */
    /* Artist Actions */
    function withdrawArtistFunds() public {
        require(msg.sender == artist, "Not artist");
        uint256 toSend = artistFund;
        artistFund = 0;
        artist.transfer(toSend);
    }

    /* Withdrawing Stuck Deposits */
    /* To reduce complexity, pull funds are entirely separate from current deposit */
    function withdrawPullFunds() public {
        require(pullFunds[msg.sender] > 0, "No pull funds available.");
        uint256 toSend = pullFunds[msg.sender];
        pullFunds[msg.sender] = 0;
        msg.sender.transfer(toSend);
    }

    /* internal */
    function _withdrawDeposit(uint256 _wei) internal {
        // note: can withdraw whole deposit, which puts it in immediate to be foreclosed state.
        require(deposit >= _wei, 'Withdrawing too much');

        deposit = deposit.sub(_wei);
        msg.sender.transfer(_wei); // msg.sender == patron

        _forecloseIfNecessary();
    }

    // Checks if the Artwork has to be foreclosed -> deposit == 0
    function _forecloseIfNecessary() internal {
        // if the artwork has not been sold
        if (before_first_sale == true){
            address currentOwner = art.ownerOf(tokenID);
            transferArtworkTo(currentOwner, artist, 0);
            emit LogForeclosure(currentOwner);
        }

        else if(deposit == 0) {
            // become Pennyworth of artwork (aka foreclose)
            address currentOwner = art.ownerOf(tokenID);
            transferArtworkTo(currentOwner, address(this), 0);
            emit LogForeclosure(currentOwner);
        }
    }

    // transfers the artwork from the current owner to the new owner 
    function transferArtworkTo(address _currentOwner, address _newOwner, uint256 _newPrice) internal {        
        art.transferFrom(_currentOwner, _newOwner, tokenID);

        price = _newPrice;
        timeAcquired = now;
    }

}
