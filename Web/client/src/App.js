import React, { Component } from "react";
import PennyworthContract from "./contracts/PennyWorth.json";
import ERC721 from "./contracts/ERC721.json"
import getWeb3 from "./getWeb3";
// import truffleContract from "truffle-contract";
import "./App.css";
import Web3 from "web3";

class App extends Component {
  state = { storageValue: "", 
            web3: null, 
            accounts: null, 
            pennyContract: null, 
            ercContract: null,
            ercAdress: "", 
            pennyAdress: "",
            name: "", 
            tokenID: "",
            tokenURI: "", 
            symbol: "",
            artistAdress: "", 
            artworkAdress: "", 
            patronage: "",
            pennyPrice: "",
            newPrice: "",
            newDeposit: "",
            };

  componentDidMount = async () => {
    try {

      // Binding functions
      // this.handlegetPennyDeposit = this.handlegetPennyDeposit.bind(this)
      this.handlePennyWorthBuy = this.handlePennyWorthBuy.bind(this)
      this.handlegetPrice = this.handlegetPrice.bind(this)
      this.handlePennyWorthConnect = this.handlePennyWorthConnect.bind(this)
      this.handleArtworkConnect = this.handleArtworkConnect.bind(this)
      this.handlegetArtistAdress = this.handlegetArtistAdress.bind(this)
      this.handlegetArtworkAdress = this.handlegetArtworkAdress.bind(this)
      this.handlegetArtworkSteward = this.handlegetArtworkSteward.bind(this)
      this.handlegetArtworkTokenId = this.handlegetArtworkTokenId.bind(this)
      this.handlegetArtworkInitStatus = this.handlegetArtworkInitStatus.bind(this)
      this.handleChange = this.handleChange.bind(this); 
      this.handleArtworkSubmit = this.handleArtworkSubmit.bind(this);
      this.handlePennyWorthSubmit = this.handlePennyWorthSubmit.bind(this)
      // Get network provider and web3 instance.
      const web3 = await getWeb3();

      // Use web3 to get the user's accounts.
      const accounts = await web3.eth.getAccounts();

      // LEGACY ----
      // Get the contract instance.
      // const networkId = await web3.eth.net.getId();
      // const deployedNetwork = SimpleStorageContract.networks[networkId];
      // Contract is called by JSON interface, [, adress] [, options]
      //const instance = new web3.eth.Contract(
      //  SimpleStorageContract.abi,
      //  deployedNetwork && deployedNetwork.address,
      //); ----

      // Set web3, accounts, and contract to the state, and then proceed with an
      // example of interacting with the contract's methods.
      this.setState({ web3, accounts, });
    } catch (error) {
      // Catch any errors for any of the above operations.
      alert(
        `Failed to load web3, accounts, or contract. Check console for details.`,
      );
      console.error(error);
    }
  };

  handleChange(event){
    
    this.setState({[event.target.name] : event.target.value})
  }


  async handleArtworkSubmit(event) {
    // this function generates the ERC721 contract from which the can be minted
    event.preventDefault();
    
    const { accounts, contract, web3 } = this.state; 
    console.log("Creating Artwork / Deploying ERC721 contract")
    console.log(this.state);
    const newContract = new web3.eth.Contract(
      ERC721.abi);
    // deploy this new contract to the network
    const deployed = await newContract.deploy({data: ERC721.bytecode, 
      arguments: [this.state.tokenID, this.state.name, this.state.symbol, this.state.tokenURI
      ]}).send({from:accounts[0]})
    console.log("ERC721 deployed at: ", deployed._address)
    // set the deployed artwork into the app state
    this.setState({ercContract: deployed})
  }

  async handleArtworkConnect(event){
    // this connects to an existing Artwork / ERC Contract
    event.preventDefault();
    const { web3, accounts, contract, ercAdress } = this.state; 
    console.log("passed contract adress: ", ercAdress)
    // get current network 
    const networkId = await web3.eth.net.getId();
    // create artwork instance with that networkId and the Artwork adress, using the jsonInterface of the Artwork
    const instance = new web3.eth.Contract(
      ERC721.abi,
      ercAdress,
    );
    // set the new instance 
    this.setState({ercContract: instance})
    // get info from new contract
    // this.setState({tokenID: this.state.ercContract.tokenID})
    // console.log(this.state.tokenID)
  }

  async handlegetArtworkInitStatus(){
    // gets the init status from a deployed erc721 by using the getter function automatically created by sol
    const { ercContract, accounts, contract } = this.state; 
    const response = await ercContract.methods.init().call({from: accounts[0]});
    console.log("artwork status is: ", response);
  }

  async handlegetArtworkTokenId(){
    // gets the tokenID from a deployed erc721 by using the getter function automatically created by sol
    const { ercContract, accounts, contract } = this.state; 
    const response = await ercContract.methods.tokenID().call({from: accounts[0]});
    console.log("artwork tokenID is: ", response);
  }

  async handlegetArtworkSteward(){
    // gets the steward from a deployed erc721 by using the getter function automatically created by sol
    // if the artwork has not been minted / setup func not used, artwork will return an "empty" address
    const { ercContract, accounts, contract } = this.state; 
    const response = await ercContract.methods.steward().call({from: accounts[0]});
    console.log("artwork steward is: ", response)
  }

  async handlegetArtworkAdress(){
    // gets the adress from the deployed artwork that is currently stored in the state
    const { ercContract, accounts, contract } = this.state; 
    console.log("artwork adress is: ", ercContract._address)
  }

  async handlePennyWorthSubmit(event){
    const { accounts, contract, web3 } = this.state; 
    event.preventDefault();
    console.log(this.state)
    console.log("Creating PennyWorth Contract")
    // Creating new contract instance -- not deployed yet
    const newContract = new web3.eth.Contract(
      PennyworthContract.abi);
    // deploy this new contract to the network
    const deployed = await newContract.deploy({data: PennyworthContract.bytecode, 
      arguments: [this.state.artistAdress, this.state.artworkAdress, this.state.tokenID, this.state.patronage
      ]}).send({from:accounts[0]})
    console.log("PennyWorth deployed at: ", deployed._address)
    // set the deployed artwork into the app state
    this.setState({pennyContract: deployed})
    // Set the price to be displayed
    const price = await this.handlegetPrice()
    this.setState({pennyPrice: price})
  }
  async handlePennyWorthConnect(event){
    // this connects to an existing Artwork / ERC Contract
    event.preventDefault();
    const { web3, accounts, contract, pennyAdress } = this.state; 
    console.log("passed penny adress: ", pennyAdress)
    // get current network 
    const networkId = await web3.eth.net.getId();
    // create artwork instance with that networkId and the Artwork adress, using the jsonInterface of the Artwork
    const instance = new web3.eth.Contract(
      PennyworthContract.abi,
      pennyAdress,
    );
    // set the new instance 
    this.setState({pennyContract: instance})
    // Set the price to be displayed
    const price = await this.handlegetPrice()
    this.setState({pennyPrice: price})
  }

  async handlegetArtistAdress(){
    // returns the adress of the artist associated with the pennyworth contract 
    const { pennyContract, accounts, contract } = this.state; 
    const response = await pennyContract.methods.artist().call({from: accounts[0]});
    console.log("artist receiving patronage is: ", response)
    const price = await this.handlegetPrice()
    console.log("price", price)
  }

  async handlegetPatronage(){
    // returns the patronage as percentage
    const { pennyContract, accounts, contract } = this.state; 
    const response = await pennyContract.methods.patronageNumerator().call({from: accounts[0]});
    console.log("patronage is: ", response)
  }

  async handlegetPrice(){
    const { pennyContract, accounts, contract } = this.state; 
    const response = await pennyContract.methods.price().call({from: accounts[0]});
    return response
  }

  async handlePennyWorthBuy(event){
    event.preventDefault();
    const { pennyContract, accounts, contract } = this.state; 
    await pennyContract.methods.buy(this.state.newPrice, this.state.pennyPrice).send(
      {from : accounts[0],
       value: this.state.newDeposit
      }
    )
    // Set the price to be displayed
    const price = await this.handlegetPrice()
    this.setState({pennyPrice: price})
  }

  async handlegetPennyDeposit(){
    const { pennyContract, accounts, contract } = this.state; 
    const response = await pennyContract.methods.deposit().call({from: accounts[0]});
    return console.log("deposit: ", response)

  }

  handlegetPennyAdress(){
    // gets the adress from the deployed artwork that is currently stored in the state
    console.log("trying to get pennyworth adress")
    const { pennyContract, accounts, contract } = this.state; 
    console.log("artwork adress is: ", pennyContract._address)
  }

  render() {
    console.log("render");
    if (!this.state.web3) {
      return <div>Loading Web3, accounts, and contract...</div>;
    }
    return (
      <div className="App">
        <h1>Welcome to this dapp!</h1>
        <h2> This form will create the Artwork </h2>
        <form onSubmit={this.handleArtworkSubmit}>
        <input name="name" placeholder="name" value={this.state.name} onChange={this.handleChange}/>
        <input name="tokenID" placeholder="tokenID" value={this.state.tokenID} onChange={this.handleChange}/>
        <input name="symbol" placeholder="symbol" value={this.state.symbol} onChange={this.handleChange}/>
        <input name="tokenURI" placeholder="token uri" value={this.state.tokenURI} onChange={this.handleChange}/>
        <input type="submit" value="create contract"/>
        </form>
        <h2> If you want to connect to an existing Artwork, you can use this form instead</h2>
        <form onSubmit={this.handleArtworkConnect}>
        <input name="ercAdress" placeholder="Adress ERC Contract" value={this.state.ercAdress} onChange={this.handleChange}/>
        <input type="submit" value="connect to contract"/>
        </form>
        <h4> Methods to be called on the Artwork</h4>
        <button onClick={() => this.handlegetArtworkInitStatus()}>get init status</button>
        <button onClick={() => this.handlegetArtworkTokenId()}>get token id</button>
        <button onClick={() => this.handlegetArtworkSteward()}>get artwork steward</button>
        <button onClick={() => this.handlegetArtworkAdress()}>get artwork adress</button>
        <h2> This form will create your PennyWorth Contract which controls the Artwork </h2>
        <form onSubmit={this.handlePennyWorthSubmit}>
        <input name="artistAdress" placeholder="Adress of the Artist" value={this.state.artistAdress} onChange={this.handleChange}/>
        <input name="artworkAdress" placeholder="Adress of the Artwork" value={this.state.artworkAdress} onChange={this.handleChange}/>
        <input name="tokenID" placeholder="tokenID" value={this.state.tokenID} onChange={this.handleChange}/>
        <input name="patronage" placeholder="patronage in %" value={this.state.patronage} onChange={this.handleChange}/>
        <input type="submit" value="create contract"/>
        </form>
        <h2> If you want to connect to an existing PennyWorth Contract, you can use this form instead</h2>
        <form onSubmit={this.handlePennyWorthConnect}>
        <input name="pennyAdress" placeholder="Adress PennyWorth Contract" value={this.state.pennyAdress} onChange={this.handleChange}/>
        <input type="submit" value="connect to contract"/>
        </form>
        <h4> Methods to be called on the Artwork</h4>
        <button onClick={() => this.handlegetArtistAdress()}>get artist adress</button>
        <button onClick={() => this.handlegetPatronage()}>get patronage</button>
        <button onClick={() => this.handlegetArtworkAdress()}>get artwork adress</button>
        <button onClick={() => this.handlegetPennyAdress()}>get PennyWorth adress</button>
        <button onClick={() => this.handlegetPennyDeposit()}>get Penny Deposit adress</button>
        <h3> This allows you to buy and sell an Artwork, connect to corresponding Pennyworth first</h3>
        <form onSubmit={this.handlePennyWorthBuy}> 
        <input id="price" type="text" value={"curr price: " + this.state.pennyPrice} readOnly></input>
        <input name="newPrice" placeholder="buy price" value={this.state.newPrice} onChange={this.handleChange}/>
        <input name="newDeposit" placeholder="deposit" value={this.state.newDeposit} onChange={this.handleChange}/>
        <input type="submit" value="buy Artwork"/>
        </form>
      </div>
    );
  }
}

export default App;
