import React from "react";
import {
    Container,
    Divider,
    Dropdown,
    Grid,
    Header,
    Image,
    List,
    Menu,
    Segment
} from "semantic-ui-react";
import {Link, withRouter} from "react-router-dom";
import {connect} from "react-redux";
import {logout} from "../store/actions/auth";
import {fetchCart} from "../store/actions/cart";

class CustomLayout extends React.Component {
    componentDidMount() {
        this.props.fetchCart();
    }

    render() {
        const {authenticated, cart, loading} = this.props;
        return (
            <div>
                <Menu inverted>
                    <Container>
                        <Link to="/">
                            <Menu.Item header>Home</Menu.Item>
                        </Link>
                        <Link to="/products">
                            <Menu.Item header>Products</Menu.Item>
                        </Link>
                        {authenticated ? (
                            <React.Fragment>
                                <Menu.Menu position="right">
                                    <Link to="/profile">
                                        <Menu.Item>Profile</Menu.Item>
                                    </Link>
                                    <Dropdown
                                        icon="cart"
                                        loading={loading}
                                        text={`${cart !== null ? cart.order_items.length : 0}`}
                                        pointing
                                        className="link item"
                                    >
                                        <Dropdown.Menu>
                                            {cart !== null ? (
                                                <React.Fragment>
                                                    {cart.order_items.map(order_item => {
                                                        return (
                                                            <Dropdown.Item key={order_item.id}>
                                                                {order_item.quantity} x {order_item.item.title}
                                                            </Dropdown.Item>
                                                        );
                                                    })}
                                                    {cart.order_products.length < 1 ? (
                                                        <Dropdown.Item>No Products in your cart</Dropdown.Item>
                                                    ) : null}
                                                    <Dropdown.Divider/>

                                                    <Dropdown.Item
                                                        icon="arrow right"
                                                        text="Checkout"
                                                        onClick={() =>
                                                            this.props.history.push("/order-summary")
                                                        }
                                                    />
                                                </React.Fragment>
                                            ) : (
                                                <Dropdown.Item>No items in your cart</Dropdown.Item>
                                            )}
                                        </Dropdown.Menu>
                                    </Dropdown>
                                    <Menu.Item header onClick={() => this.props.logout()}>
                                        Logout
                                    </Menu.Item>
                                </Menu.Menu>
                            </React.Fragment>
                        ) : (
                            <Menu.Menu position="right">
                                <Link to="/login">
                                    <Menu.Item header>Login</Menu.Item>
                                </Link>
                                <Link to="/signup">
                                    <Menu.Item header>Signup</Menu.Item>
                                </Link>
                            </Menu.Menu>
                        )}
                    </Container>
                </Menu>

                {this.props.children}

                <Segment
                    inverted
                    vertical
                    style={{margin: "5em 0em 0em", padding: "5em 0em"}}
                >
                    <Container textAlign="center">
                        <Divider inverted section/>
                        <Image centered size="mini"
                               src="https://www.pinclipart.com/picdir/middle/307-3071078_call-contact-dial-communication-svg-png-icon-.png"/>
                        <List horizontal inverted divided link size="small">
                            <List.Item as="a" href="#">
                                Site Map
                            </List.Item>
                            <List.Item as="a" href="#">
                                Contact Us
                            </List.Item>
                            <List.Item as="a" href="#">
                                Terms and Conditions
                            </List.Item>
                            <List.Item as="a" href="#">
                                Privacy Policy
                            </List.Item>
                        </List>
                    </Container>
                </Segment>
            </div>
        );
    }
}

const mapStateToProps = state => {
    return {
        authenticated: state.auth.token !== null,
        cart: state.cart.shoppingCart,
        loading: state.cart.loading
    };
};

const mapDispatchToProps = dispatch => {
    return {
        logout: () => dispatch(logout()),
        fetchCart: () => dispatch(fetchCart())
    };
};

export default withRouter(
    connect(
        mapStateToProps,
        mapDispatchToProps
    )(CustomLayout)
);