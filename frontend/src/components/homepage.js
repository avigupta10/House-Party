import RoomJoinPage from './roomjoinpage';
import CreateRoomPage from './createroompage';
import Room from './room';

import {useEffect, useState} from "react";
import {BrowserRouter, Route, Switch, Redirect, Link} from "react-router-dom";
import {Grid, Button, ButtonGroup, Typography} from '@material-ui/core'

function Homepage() {
    const [room_code, codeSet] = useState(null)

    useEffect( () => {
        fetch('/api/user-in-room').then((response) => response.json()).then((data) => {
            codeSet(data.code)
        })
    },[])

    const clearRoomCode = () => {
        codeSet(null)
    }

    return (
        <BrowserRouter>
            <Switch>
                <Route exact path="/" render={() => {
                    return room_code ? (<Redirect to={`/room/${room_code}`} /> ) : (renderHomePage());
                }} />
                <Route path="/join" component={RoomJoinPage}/>
                <Route path="/create" component={CreateRoomPage}/>
                <Route path="/room/:code" render={(props) => {
                    return <Room {...props} leaveRoomCallback={clearRoomCode}/>
                }} />
            </Switch>
        </BrowserRouter>
    );
}

function renderHomePage() {
    return (
        <Grid container spacing={3} align='center'>
            <Grid item xs={12}>
                <Typography variant='h3' component='h3'>
                    House Party
                </Typography>
            </Grid>
            <Grid item xs={12}>
                <ButtonGroup disableElevation variant='contained' color='primary'>
                    <Button color='primary' to='/join' component={Link}>
                        Join a Room
                    </Button>
                    <Button color='secondary' to='/create' component={Link}>
                        Create a Room
                    </Button>
                </ButtonGroup>
            </Grid>
        </Grid>
    );
}

export default Homepage;