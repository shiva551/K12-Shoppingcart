import React from "react";
import { Route } from "react-router-dom";
import Hoc from "./hoc/hoc";

import Login from "./components/Login";
import Signup from "./components/Signup";
import HomepageLayout from "./components/Home";
import ProductList from "./components/ProductList";
import ProductDetail from "./components/ProductDetail";
import OrderSummary from "./components/OrderSummary";
import Checkout from "./components/Checkout";
import Profile from "./components/Profile";

const BaseRouter = () => (
  <Hoc>
    <Route exact path="/products" component={ProductList} />
    <Route path="/products/:productID" component={ProductDetail} />
    <Route path="/login" component={Login} />
    <Route path="/signup" component={Signup} />
    <Route path="/order-summary" component={OrderSummary} />
    <Route path="/checkout" component={Checkout} />
    <Route path="/profile" component={Profile} />
    <Route exact path="/" component={HomepageLayout} />
  </Hoc>
);

export default BaseRouter;