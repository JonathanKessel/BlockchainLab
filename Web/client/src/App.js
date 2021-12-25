import React, { Component } from "react";
import SimpleStorageContract from "./contracts/SimpleStorage.json";
import getWeb3 from "./getWeb3";
import truffleContract from "truffle-contract";
import "./App.css";
import Web3 from "web3";

class App extends Component {
  state = { storageValue: "", web3: null, accounts: null, contract: null, newValue: "", contractValue: ""};

  componentDidMount = async () => {
    try {

      this.handleChange = this.handleChange.bind(this); 
      this.handleSubmit = this.handleSubmit.bind(this);
      this.handleContractDeploymentSubmit = this.handleContractDeploymentSubmit.bind(this);
      // Get network provider and web3 instance.
      const web3 = await getWeb3();

      // Use web3 to get the user's accounts.
      const accounts = await web3.eth.getAccounts();

      // Get the contract instance.
      const networkId = await web3.eth.net.getId();
      const deployedNetwork = SimpleStorageContract.networks[networkId];
      // Contract is called by JSON interface, [, adress] [, options]
      const instance = new web3.eth.Contract(
        SimpleStorageContract.abi,
        deployedNetwork && deployedNetwork.address,
      );

      // Set web3, accounts, and contract to the state, and then proceed with an
      // example of interacting with the contract's methods.
      this.setState({ web3, accounts, contract: instance }, this.runExample);
    } catch (error) {
      // Catch any errors for any of the above operations.
      alert(
        `Failed to load web3, accounts, or contract. Check console for details.`,
      );
      console.error(error);
    }
  };

  handleChange(event){
    
    this.setState({newValue: event.target.value});
    console.log(this.state.newValue);
  }

  async handleContractChange(event){
    this.setState({contractValue: event.target.value});
    
  }

  async handleSubmit(event){
    event.preventDefault();
    
    const { accounts, contract } = this.state; 
    console.log("handle triggered")
    console.log("contract: ", contract)
    // console.log("value", this.state.newValue)
    // Interacts with smart contract method "set" via the .methods attribute
    await contract.methods.set(this.state.newValue).send({from: accounts[0]});

    // Gets the updatet info of the contract via .get() function, careful this is a call function since we dont alter the state of the smart contract
    const response = await contract.methods.get().call({from: accounts[0]});
    console.log("value: ", response)
    // set response into state and display that response (since state changes, SS will reload)
    this.setState({storageValue: response});

  }

  async handleContractDeploymentSubmit(event){
    event.preventDefault();
    const { web3, accounts, contract } = this.state; 
    // create new Contract instance based on sol code without an adress since we have not deployed yet
    const newContract = new web3.eth.Contract(
      SimpleStorageContract.abi);
    // deploy this new contract to the network
    const deployed = await newContract.deploy({data: SimpleStorageContract.bytecode, arguments: ['schokolade']}).send({from:accounts[0]})
    console.log("adress: ", deployed._address)

    // create new contract instance
    const instance = new web3.eth.Contract(
      SimpleStorageContract.abi,
      deployed._address
    );
    // set this new contract as default contract to be looked into
    this.setState({contract: instance})
    // get the new stored value and display it by loading it into the state
    const response = await instance.methods.get().call({from: accounts[0]});
    console.log("response (should be schokolade): ", response)
    // set response into state and display that response (since state changes, SS will reload)
    this.setState({storageValue: response});
  }


  runExample = async () => {
    const { contract } = this.state;

    // Get the value from the contract to prove it worked.
    const response = await contract.methods.get().call();

    // Update state with the result.
    this.setState({ storageValue: response });
  };

  render() {
    console.log("render");
    if (!this.state.web3) {
      return <div>Loading Web3, accounts, and contract...</div>;
    }
    return (
      <div className="App">
        <h1>Welcome to this dapp!</h1>
        <h2> This form will take an argument, transact it to the blockchain and display it</h2>
        <div > Stored Argument: {this.state.storageValue}</div>
        <div style={{marginBottom: '100px'}}>
        <form onSubmit={this.handleSubmit}> 
          <input type="text" value={this.state.newValue} onChange={this.handleChange.bind(this)}/>
          <input type="submit" value="Submit"/>
        </form>
        </div>
        <h2> This form will create a new instance with the argument passed by the constructor</h2>
        <div>
        <form onSubmit={this.handleContractDeploymentSubmit}> 
          <input type="submit" value="Submit"/>
        </form>
        </div>

      </div>
    );
  }
}

export default App;
