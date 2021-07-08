import {Button, Grid, TextField, Typography} from '@material-ui/core';
import {Link} from 'react-router-dom';
import {useState} from "react";

function RoomJoinPage(props) {
    const [code, setCode] = useState("")
    const [error, setError] = useState("")

    const codeOnChange = (e) => {
        setCode(e.target.value)
    }

    const roomButtonClicked = () => {
        const options = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                code: code
            })
        }
        fetch('/api/join-room', options).then((response) => {
            if (response.ok) {
                props.history.push(`/room/${code}`)
            } else {
                setError('Room Not Found')
            }
        }).catch((error) => console.error(error))
    }

    return (
        <Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Typography variant='h4' component='h4'>
                    Join a Room
                </Typography>
            </Grid>
            <Grid item xs={12} align="center">
                <TextField error={error} label='Code' placeholder='Enter a RoomCode' value={code} helperText={error}
                           variant='outlined' onChange={codeOnChange}/>
            </Grid>
            <Grid item xs={12} align="center">
                <Button variant='contained' color='primary' onClick={roomButtonClicked}>Enter Room</Button>
            </Grid>
            <Grid item xs={12} align="center">
                <Button variant='contained' color='secondary' to='/' component={Link}>Back</Button>
            </Grid>
        </Grid>
    );
}

export default RoomJoinPage;