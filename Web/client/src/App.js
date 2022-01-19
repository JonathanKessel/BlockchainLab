import React, { Component, useState } from 'react';
import PennyworthContract from "./contracts/PennyWorth.json";
import ERC721 from "./contracts/ERC721.json"
import getWeb3 from './getWeb3';
// import truffleContract from "truffle-contract";
import './App.css';
import 'bootstrap/dist/css/bootstrap.css';
import Web3 from "web3";
import { Alert, Form, Button, Container, Row, Col, InputGroup, ButtonGroup, Table } from 'react-bootstrap';
import { create as ipfsHttpClient} from 'ipfs-http-client'

/* Create an instance of the client */
const client = ipfsHttpClient('https://ipfs.infura.io:5001/api/v0')

class App extends Component {
  state = { storageValue: "", 
            web3: null, 
            accounts: null, 
            pennyContract: {}, //or set to null, still need to figure out whats better
            pennyContractAdress: '',
            pennyPatronage: '',
            pennyArtistAdress: '',
            pennyDeposit: '',
            pennyPrice: '',
            pennyContractAdress: '',          
            ercContract: null,
            ercAdress: '', 
            pennyAdress: '',
            name: "", 
            tokenID: "",
            tokenURI: "", 
            symbol: "",
            artistAdress: "", 
            artworkAdress: "",
            artworkInitStatus: false,
            artworkTokenID: "",
            artworkSteward: "",
            patronage: "",
            pennyPrice: "",
            newPrice: "",
            newDeposit: "",
            fileURL: '',
            file: {},
            alertVisibilityForm1: false,
            alertVisibilityForm2: false,
            alertVisibilityForm3: false,
            alertVisibilityForm4: false,
            Form1Loader:false,
            Form3Loader:false,
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
      this.handlePennyWorthSubmit = this.handlePennyWorthSubmit.bind(this);
      this.handleInfuraUpload = this.handleInfuraUpload.bind(this);
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
  
  async handleInfuraUpload (event) {
    const file = event.target.files[0]
   // const file = this.state.file

    try {
      const added = await client.add(file)
      const url = `https://ipfs.infura.io/ipfs/${added.path}`
      this.setState({fileURL : url});
      console.log(url);
      console.log(this.state.fileURL)
    } catch (error) {
      console.log('Error uploading the file : ', error)
    }
  }

  async handleArtworkSubmit(event) {
    // set Form loader to "creating" alias spinning
    this.setState({Form1Loader:true})
    // this function generates the ERC721 contract from which the can be minted
    event.preventDefault();
    
    const { accounts, contract, web3 } = this.state; 
    console.log("Creating Artwork / Deploying ERC721 contract")
    console.log(this.state);
    const newContract = new web3.eth.Contract(
      ERC721.abi);
    // deploy this new contract alias asset to the network
    const deployed = await newContract.deploy({data: ERC721.bytecode, 
      arguments: [this.state.tokenID, this.state.name, this.state.symbol, this.state.fileURL
      ]}).send({from:accounts[0]})

    console.log("ERC721 deployed at: ", deployed._address)
    this.setState({Form1Loader:false})
    // set the deployed artwork into the app state
    this.setState({ercContract: deployed})
    this.setState({ercAdress: deployed._address})
    // show Alert with processing meta data
    this.setState({alertVisibilityForm1:true})
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
    console.log(this.state.tokenID)
    this.handlegetArtworkInitStatus()
    this.handlegetArtworkTokenId()
    this.handlegetArtworkSteward()
    this.handlegetArtworkAdress() 
    // show Alert with processing meta data
    this.setState({alertVisibilityForm2:true});
  }

  async handlegetArtworkInitStatus(){
    // gets the init status from a deployed erc721 by using the getter function automatically created by sol
    const { ercContract, accounts, contract } = this.state; 
    const response = await ercContract.methods.init().call({from: accounts[0]});
    this.setState({artworkInitStatus: response});
    console.log("artwork status is: ", response);
  }

  async handlegetArtworkTokenId(){
    // gets the tokenID from a deployed erc721 by using the getter function automatically created by sol
    const { ercContract, accounts, contract } = this.state; 
    const response = await ercContract.methods.tokenID().call({from: accounts[0]});
    this.setState({artworkTokenID: response}); //store TokenID in separete State value. Redundant Information in ercContract-State-Object, but will work temporarily
    console.log("artwork tokenID is: ", response);
  }

  async handlegetArtworkSteward(){
    // gets the steward from a deployed erc721 by using the getter function automatically created by sol
    // if the artwork has not been minted / setup func not used, artwork will return an "empty" address
    const { ercContract, accounts, contract } = this.state; 
    const response = await ercContract.methods.steward().call({from: accounts[0]});
    console.log("artwork steward is: ", response)
    this.setState({artworkSteward: response}); //store artworkSteward in separete State value. Redundant Information in ercContract-State-Object, but will work temporarily
  }

  async handlegetArtworkAdress(){
    // gets the adress from the deployed artwork that is currently stored in the state
    const { ercContract, accounts, contract } = this.state; 
    console.log("artwork adress is: ", ercContract._address)
    this.setState({artworkAdress: ercContract._address}); //store ercAdress in separate State value. Redundant Information in ercContract-State-Object, but will work temporarily
  }

  async handlePennyWorthSubmit(event){
    this.setState({Form3Loader:true})
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
    this.setState({Form3Loader:true})
    console.log("PennyWorth deployed at: ", deployed._address)
    this.setState({pennyContractAdress: deployed._adress})
    // set the deployed artwork into the app state
    this.setState({pennyContract: deployed})
    // Set the price to be displayed
    const price = await this.handlegetPrice()
    this.setState({pennyPrice: price})
    // show Alert with processing meta data
    this.setState({alertVisibilityForm3:true});
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

    // trigger GET Methods for displaying additional information
    this.handlegetArtistAdress()
    this.handlegetPatronage()
    this.handlegetArtworkAdress()
    this.handlegetPennyAdress()
    this.handlegetPennyDeposit()

    // show Alert with processing meta data
    this.setState({alertVisibilityForm4:true});
  }

  async handlegetArtistAdress(){
    // returns the adress of the artist associated with the pennyworth contract 
    const { pennyContract, accounts, contract } = this.state; 
    const response = await pennyContract.methods.artist().call({from: accounts[0]});
    console.log("artist receiving patronage is: ", response)
    this.setState({pennyArtistAdress: response})
    const price = await this.handlegetPrice()
    console.log("price", price)
  }

  async handlegetPatronage(){
    // returns the patronage as percentage
    const { pennyContract, accounts, contract } = this.state; 
    const response = await pennyContract.methods.patronageNumerator().call({from: accounts[0]});
    this.setState({pennyPatronage: response})
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
    this.setState({pennyDeposit: response})
    return console.log("deposit: ", response)

  }

  handlegetPennyAdress(){
    // gets the adress from the deployed artwork that is currently stored in the state
    console.log("trying to get pennyworth adress")
    const { pennyContract, accounts, contract } = this.state;
    this.setState({pennyAdress: pennyContract._address})
    console.log("artwork adress is: ", pennyContract._address)
  }
  
  onDismissAlert = ()=>{
    this.setState({
      alertVisibilityForm1: false,
      alertVisibilityForm2: false,
      alertVisibilityForm3: false,
      alertVisibilityForm4: false
    });
  }

  render() {
    console.log("rendering ...");
    if (!this.state.web3) {
      return (
        <div className="col-lg-8 mx-auto p-3 py-md-5">
          <Alert variant="info">
            <Alert.Heading>Preparing Environment</Alert.Heading>
            <p>
            <span role="img">🚧</span> Loading Web3, accounts, and contract ...
            </p>
            <hr />
            <p className="mb-0">
            Make sure to enable the MetaMask Extension in your Browser and grant this site access to your IDs.
            </p>
          </Alert>
        </div>
      )
    }
    return (

      <div className="App col-lg-8 mx-auto p-3 py-md-5">
        <Container>
          <Row>
            <div className="d-flex align-items-center pt-3 pb-3 mt-3 mb-3 border-bottom">
              <a href="/" className="d-flex align-items-center text-dark text-decoration-none">
                <h1>🖼 NFT Admin</h1>
              </a>
            </div>
          </Row>
            <div className="d-flex align-items-center pb-3 mb-5 border-bottom">
              <p>Manage your NFT Assets based on Harberger Tax Model with this Web application.</p>
            </div>
          <Row className="mb-2 mt-2">
            <Col className="p-5 mx-2 border rounded">
              <h2>Create a new Artwork</h2>
              <Form onSubmit={this.handleArtworkSubmit}>
                <Form.Group as={Row} className="mb-3 mt-5" controlId="formCreateNewArtworkName">
                  <Form.Label column sm={2}>Name</Form.Label>
                  <Col sm={10}>
                    <Form.Control name="name" type="text" placeholder="my Awesome Artwork" value={this.state.name} onChange={this.handleChange}/>
                    </Col>
                </Form.Group>
                <Form.Group as={Row} className="mb-3" controlId="formCreateNewArtworkTokenID">
                  <Form.Label column sm={2}>Token ID</Form.Label>
                  <Col sm={10}>
                  <Form.Control name="tokenID" type="number" placeholder="1234567890" value={this.state.tokenID} onChange={this.handleChange}/></Col>
                </Form.Group>
                <Form.Group as={Row} className="mb-3" controlId="formCreateNewArtworkSymbol">
                  <Form.Label column sm={2}>Symbol</Form.Label>
                  <Col sm={10}>
                  <Form.Control name="symbol" type="text" placeholder="symbol" value={this.state.symbol} onChange={this.handleChange}/></Col>
                </Form.Group>
                <Form.Group as={Row} className="mb-3" controlId="formCreateNewArtworkFile">
                  <Form.Label column sm={2}>Artwork-File</Form.Label>
                  <Col sm={10}>
                  <Form.Control name="file" type="file" onChange={(e) => this.handleInfuraUpload(e)} required /></Col>
                </Form.Group>
                <Button variant="primary" size="lg" type="submit" className="mb-3 mt-3" disabled={this.state.Form1Loader}>
                {this.state.Form1Loader ? 'Creating Artwork ...' : 'Create new Artwork'}
                </Button>
              </Form>
              <Alert className="mb-5" variant="success" show={this.state.alertVisibilityForm1} onClose={()=>{this.onDismissAlert()}} dismissible>
                <Alert.Heading>Artwork successfully created.</Alert.Heading>
                <hr />
                ERC 721 deployed to Test-Network Goerli at <code>{this.state.ercAdress}</code>
                <ButtonGroup>
                <Button variant="secondary" size="sm" type="submit" className="m-2" href={this.state.fileURL}>
                View on IPFS 🖼
                </Button>
                <Button variant="secondary" size="sm" type="submit" className="m-2" href={"https://goerli.etherscan.io/address/" + this.state.ercAdress}>
                View on Etherscan 🔍
                </Button>
                </ButtonGroup>
              </Alert>
            </Col>
            <Col className="p-5 mx-2 border rounded">
              <h2>Connect to an existing Artwork</h2>
              <Form onSubmit={this.handleArtworkConnect}>
                <Form.Group as={Row} className="mb-3 mt-5" controlId="formConnectExistingArtworkERCAdress">
                  <Form.Label column sm={2}>Adress ERC Contract</Form.Label>
                  <Col sm={10}>
                    <Form.Control name="ercAdress" type="text" placeholder="0xdd82D48E91C2944ceC6973a5b9f9a646C711d5EF" value={this.state.ercAdress} onChange={this.handleChange} required />
                    <Form.Text className="text-muted">ercAdress</Form.Text>
                    </Col>
                </Form.Group>
                <Button variant="primary" size="lg" type="submit" className="mb-3 mt-3">
                  Connect to existing Artwork
                </Button>
              </Form>
              <Alert className="mb-5" variant="success" show={this.state.alertVisibilityForm2} onClose={()=>{this.onDismissAlert()}} dismissible>
                <Alert.Heading>Connection established!</Alert.Heading>
                <hr />
                <p className="m-3">
                  See Details of the connected Artwork below.
                </p>
                <Table striped bordered hover responsive size="sm">
                  <tbody>
                    <tr>
                      <td>Init Status</td>
                      <td><code>{this.state.artworkInitStatus ? 'true' : 'false'}</code></td>
                    </tr>
                    <tr>
                      <td>TokenID</td>
                      <td><code>{this.state.artworkTokenID}</code></td>
                    </tr>
                    <tr>
                      <td>Adress</td>
                      <td><code>{this.state.artworkAdress}</code></td>
                    </tr>
                    <tr>
                      <td>Steward</td>
                      <td><code>{this.state.artworkSteward}</code></td>
                    </tr>
                  </tbody>
                </Table>
              </Alert>
            </Col>
          </Row>
          <Row className="pb-3 mb-5 pt-3">
          <Col className="p-5 mx-2 border rounded">
          <h2>Create your PennyWorth Contract which controls the Artwork</h2>
          <Form onSubmit={this.handlePennyWorthSubmit}>
            <Form.Group as={Row} className="mb-3 mt-5" controlId="formCreateNewPWContractArtistAdress">
              <Form.Label column sm={3}>Artist-Address</Form.Label>
              <Col sm={9}>
                <Form.Control name="artistAdress" type="text" placeholder="0x06012c8cf97BEaD5deAe237070F9587f8E7A266d" value={this.state.artistAdress} onChange={this.handleChange} required/>
                <Form.Text className="text-muted">adress of the artist who receives the patronage</Form.Text>
                </Col>
            </Form.Group>
            <Form.Group as={Row} className="mb-3" controlId="formCreateNewPWContractARtworkAddress">
              <Form.Label column sm={3}>Artwork-Address</Form.Label>
              <Col sm={9}>
              <Form.Control name="artworkAdress" type="text" placeholder="0x06012c8cf97BEaD5deAe237070F9587f8E7A266d" value={this.state.artworkAdress} onChange={this.handleChange} required/></Col>
            </Form.Group>
            <Form.Group as={Row} className="mb-3" controlId="formCreateNewPWContractTokenID">
              <Form.Label column sm={3}>Token ID</Form.Label>
              <Col sm={9}>
              <Form.Control name="tokenID" type="number" placeholder="8313155112" value={this.state.tokenID} onChange={this.handleChange} required/></Col>
            </Form.Group>
            <Form.Group as={Row} className="mb-3" controlId="formCreateNewPWContractPatronage">
              <Form.Label column sm={3}>Patronage</Form.Label>
              <Col sm={9}>
              <InputGroup>
                <Form.Control name="patronage" type="number" placeholder="5" value={this.state.patronage} onChange={this.handleChange} required aria-label="Patronage in %" />
                <InputGroup.Text>%</InputGroup.Text>
              </InputGroup>
              </Col>
            </Form.Group>
            <Button variant="primary" size="lg" type="submit" className="mb-3 mt-3" disabled={this.state.Form3Loader}>
                {this.state.Form3Loader ? 'Creating Contract ...' : 'Create Pennyworth Contract'}
                </Button>
          </Form>
          <Alert className="mb-5" variant="success" show={this.state.alertVisibilityForm3} onClose={()=>{this.onDismissAlert()}} dismissible>
            <Alert.Heading>Pennyworth Contract successfully created.</Alert.Heading>
            <hr />
            <p className="m-2">
            Pennyworth-Contract deployed to Test-Network Goerli at <code>{this.state.pennyContractAdress}</code> with price <code>{this.state.pennyPrice}</code></p>
            <p className="m-2">
            <ButtonGroup>
              <Button variant="secondary" size="sm" type="submit" className="m-2" href={"https://goerli.etherscan.io/address/" + this.state.pennyContract._adress}>
              View on Etherscan 🔍
              </Button>
            </ButtonGroup>
            </p>
          </Alert>
          </Col>
          <Col className="p-5 mx-2 border rounded">
          <h2>Connect to an existing PennyWorth Contract</h2>
          <Form onSubmit={this.handlePennyWorthConnect}>
            <Form.Group as={Row} className="mb-3 mt-5" controlId="formConnectExistingPWPWAdress">
              <Form.Label column sm={3}>Pennyworth-Address</Form.Label>
              <Col sm={9}>
                <Form.Control type="pennyAdress" placeholder="0x06012c8cf97BEaD5deAe237070F9587f8E7A266d" defaultValue={this.state.pennyAdress} onChange={this.handleChange} required/>
                </Col>
            </Form.Group>
            <Button variant="primary" size="lg" type="submit" className="mb-3 mt-3">
              Connect to existing Pennyworth Contract
            </Button>
          </Form>
          <Alert className="mb-5" variant="success" show={this.state.alertVisibilityForm4} onClose={()=>{this.onDismissAlert()}} dismissible>
            <Alert.Heading>Connection established!</Alert.Heading>
            <hr />
            <p className="m-3">
                  See Details of the connected Pennyworth Contract below.
                </p>
                <Table striped bordered hover responsive size="sm">
                  <tbody>
                    <tr>
                      <td>Artist Adress</td>
                      <td><code>{this.state.pennyArtistAdress}</code></td>
                    </tr>
                    <tr>
                      <td>Artwork Adress</td>
                      <td><code>{this.state.artworkAdress}</code></td>
                    </tr>
                    <tr>
                      <td>Patronage</td>
                      <td><code>{this.state.pennyPatronage}</code></td>
                    </tr>
                    <tr>
                      <td>PennyAdress</td>
                      <td><code>{this.state.pennyAdress}</code></td>
                    </tr>
                    <tr>
                      <td>Penny Deposit</td>
                      <td><code>{this.state.pennyDeposit}</code></td>
                    </tr>
                  </tbody>
                </Table>
          </Alert>
          </Col>
          </Row>
          <Row className="pb-3 mb-5 pt-3">
            <Col className="p-5 mx-2 border rounded">
            <h2>Buy and sell an Artwork</h2>
            <Alert variant="warning">
            <p className="mb-0">Connect to Corresponding Pennyworth Contract first!</p>
            </Alert>
          <Form onSubmit={this.handlePennyWorthBuy}>
            <Form.Group as={Row} className="mb-3 mt-5" controlId="formBuySellArtworkCurrentPrice">
              <Col sm={6}>
              <InputGroup>
                <InputGroup.Text>Current Price</InputGroup.Text>
                <Form.Control name="currentPrice" type="number" placeholder="" value={this.state.pennyPrice} disabled />
                <InputGroup.Text>ETH</InputGroup.Text>
              </InputGroup>
              </Col>
              <Col sm={6}>
              <InputGroup>
                <InputGroup.Text>Buy Price</InputGroup.Text>
                <Form.Control name="newprice" type="number" placeholder="42" value={this.state.newPrice} onChange={this.handleChange} required/>
                <InputGroup.Text>ETH</InputGroup.Text>
              </InputGroup>
              </Col>
            </Form.Group>
            <Form.Group as={Row} className="mb-3 mt-5" controlId="formConnectExistingPWPWAdress">
                <Form.Label column sm={3}>Pennyworth-Address</Form.Label>
                <Col sm={9}>
                  <Form.Control name="pennyAdress" type="text" value={this.state.pennyAdress}  disabled />
                  </Col>
            </Form.Group>
            <Form.Group as={Row} className="mb-3" controlId="formBuySellArtworkDeposit">
              <Form.Label column sm={3}>New Deposit</Form.Label>
              <Col sm={9}>
              <Form.Control name="newDeposit" type="number" placeholder="1535343" value={this.state.newDeposit} onChange={this.handleChange} required/></Col>
            </Form.Group>
            <Button variant="primary" size="lg" type="submit" className="mb-3 mt-3">
              Buy Artwork
            </Button>
          </Form>
          <Alert className="mb-5" variant="success" show={this.state.alertVisibilityForm4} onClose={()=>{this.onDismissAlert()}} dismissible>
            <Alert.Heading>ArtworkTrade successfully.</Alert.Heading>
            <hr />
            <p className="mb-0">
              {/* TODO: Add Metadata in Alert which is currently logged to console */}
            </p>
          </Alert>
            </Col>
          </Row>
        </Container>
        <footer className="pt-5 my-5 text-muted border-top">
          Studentisches Projekt &middot; Hochschule der Medien &middot; &copy; 2022
        </footer>
      </div>
    );
  }
}

export default App;
