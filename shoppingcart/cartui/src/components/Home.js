import PropTypes from "prop-types";
import React, {Component} from "react";
import {
    Button,
    Container,
    Divider,
    Grid,
    Header,
    Image,
    Responsive,
    Segment,
    Sidebar,
    Visibility
} from "semantic-ui-react";

const getWidth = () => {
    const isSSR = typeof window === "undefined";
    return isSSR ? Responsive.onlyTablet.minWidth : window.innerWidth;
};

class DesktopContainer extends Component {
    state = {};

    hideFixedMenu = () => this.setState({fixed: false});
    showFixedMenu = () => this.setState({fixed: true});

    render() {
        const {children} = this.props;

        return (
            <Responsive getWidth={getWidth} minWidth={Responsive.onlyTablet.minWidth}>
                <Visibility
                    once={false}
                    onBottomPassed={this.showFixedMenu}
                    onBottomPassedReverse={this.hideFixedMenu}
                />
                {children}
            </Responsive>
        );
    }
}

DesktopContainer.propTypes = {
    children: PropTypes.node
};

class MobileContainer extends Component {
    state = {};

    handleSidebarHide = () => this.setState({sidebarOpened: false});

    handleToggle = () => this.setState({sidebarOpened: true});

    render() {
        const {children} = this.props;

        return (
            <Responsive
                as={Sidebar.Pushable}
                getWidth={getWidth}
                maxWidth={Responsive.onlyMobile.maxWidth}
            >
                {children}
            </Responsive>
        );
    }
}

MobileContainer.propTypes = {
    children: PropTypes.node
};

const ResponsiveContainer = ({children}) => (
    <div>
        <DesktopContainer>{children}</DesktopContainer>
        <MobileContainer>{children}</MobileContainer>
    </div>
);

ResponsiveContainer.propTypes = {
    children: PropTypes.node
};

const HomepageLayout = () => (
    <ResponsiveContainer>
        <Segment style={{padding: "8em 0em"}} vertical>
            <Grid container stackable verticalAlign="middle">
                <Grid.Row>
                    <Grid.Column width={8}>
                        <Header as="h3" style={{fontSize: "2em"}}>
                            Online Shopping Cart
                        </Header>
                        <p style={{fontSize: "1.33em"}}>
                            We Provide Branded Items with Reasonable Price
                        </p>
                        <Header as="h3" style={{fontSize: "2em"}}>
                            Products
                        </Header>
                        <p style={{fontSize: "1.33em"}}>
                            Products
                        </p>
                    </Grid.Column>
                    <Grid.Column floated="right" width={6}>
                        <Image
                            bordered
                            rounded
                            size="large"
                            src="https://miro.medium.com/max/1100/1*D-ZiKd0B00tdifaB2X3tKQ.gif"
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                    <Grid.Column textAlign="center">
                        <Button size="huge">Check Them Out</Button>
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </Segment>
        <Segment style={{padding: "0em"}} vertical>
            <Grid celled="internally" columns="equal" stackable>
                <Grid.Row textAlign="center">
                    <Grid.Column style={{paddingBottom: "5em", paddingTop: "5em"}}>
                        <Header as="h3" style={{fontSize: "2em"}}>
                            "Online Shopping Cart"
                        </Header>
                        <p style={{fontSize: "1.33em"}}>
                            This App States Online Shopping similar like Amazon, Flipkart...
                        </p>
                    </Grid.Column>
                    <Grid.Column style={{paddingBottom: "5em", paddingTop: "5em"}}>
                        <Header as="h3" style={{fontSize: "2em"}}>
                            "Online Shopping Mall.
                            Everything Is available Here..."
                        </Header>
                        <p style={{fontSize: "1.33em"}}>
                            <Image avatar
                                   src="https://www.egapgo.com/wp-content/uploads/2019/11/online-shopping-cart-900x480.jpg"/>
                            <b>OSC</b> Online Shopping Cart
                        </p>
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </Segment>

    </ResponsiveContainer>
);
export default HomepageLayout;