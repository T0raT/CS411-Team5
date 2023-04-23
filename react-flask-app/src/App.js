import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import LandingPage from './LandingPage';
import RedirectPage from './RedirectPage';
import TopTracksAndArtists from './TopTracksAndArtists';

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/" exact component={LandingPage} />
        <Route path="/redirect" component={RedirectPage} />
        <Route path="/getTracks" component={TopTracksAndArtists} />
      </Switch>
    </Router>
  );
}

export default App;