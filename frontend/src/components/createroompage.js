import Grid from "@material-ui/core/Grid"
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import Radio from '@material-ui/core/Radio'
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Button from "@material-ui/core/Button";
import {Link} from "react-router-dom";
import {useState} from 'react'
import {Collapse} from "@material-ui/core";
import {Alert} from "@material-ui/lab";


function CreateRoomPage(props) {
    const [guest_can_pause, setPause] = useState(props.guest_can_pause)
    const [votes_to_skip, setVotes] = useState(props.votes_to_skip)
    const [errorMsg, setError] = useState('')
    const [successMsg, setSuccess] = useState('')

    const VotesOnChange = (e) => {
        setVotes(e.target.value)
    }

    const PauseOnChange = (e) => {
        setPause(e.target.value === 'true')
    }

    const RoomButtonClicked = () => {
        const options = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                votes_to_skip: votes_to_skip,
                guest_can_pause: guest_can_pause
            })
        }
        fetch('/api/create-room', options)
            .then((response) => response.json())
            .then((data) => props.history.push('/room/' + data.code));
    }

    const UpdateButtonClick = () => {
        const options = {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                votes_to_skip: votes_to_skip,
                guest_can_pause: guest_can_pause,
                code: props.code
            })
        }
        fetch('/api/settings-room', options)
            .then((response) => {
                if (response.ok) {
                    setSuccess('Room Updated Successfully')
                } else {
                    setError('Error Updating Room')
                }
                props.updateCallback();
            })

    }

    function renderCreateButtons() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Button color="primary" variant="contained" onClick={RoomButtonClicked}>Create A Room</Button>
                </Grid>
                <Grid item xs={12} align="center">
                    <Button color="secondary" variant="contained" to='/' component={Link}>Back</Button>
                </Grid>
            </Grid>
        );
    }

    function renderUpdateButtons() {
        return (
            <Grid item xs={12} align="center">
                <Button color="primary" variant="contained" onClick={UpdateButtonClick}>Update Room</Button>
            </Grid>
        );
    }

    return (
        <Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Collapse in={errorMsg !== '' || successMsg !== ''}>
                    {successMsg !== '' ? (<Alert severity='success' onClose={() => {
                        setSuccess('')
                    }}>{successMsg}</Alert>) : (<Alert severity='danger' onClose={() => {
                        setError('')
                    }}>{errorMsg}</Alert>)}
                </Collapse>
            </Grid>
            <Grid item xs={12} align="center">
                <Typography component='h4' variant='h4'>
                    {props.update ? "Settings Room" : "Create a Room"}
                </Typography>
            </Grid>
            <Grid item xs={12} align="center">
                <FormControl component='fieldset'>
                    <FormHelperText>
                        <div align="center">
                            Guest Control of Playback State
                        </div>
                    </FormHelperText>
                    <RadioGroup row defaultValue={props.guest_can_pause.toString()} onChange={PauseOnChange}>
                        <FormControlLabel value='true' control={<Radio color='primary'/>} label='Play/Pause'
                                          labelPlacement='bottom'/>
                        <FormControlLabel value='false' control={<Radio color='secondary'/>} label='No Control'
                                          labelPlacement='bottom'/>
                    </RadioGroup>
                </FormControl>
            </Grid>
            <Grid item xs={12} align="center">
                <FormControl>
                    <TextField required='true' type="number" defaultValue={props.votes_to_skip} onChange={VotesOnChange}
                               inputProps={{min: 1, style: {textAlign: 'center'}}}/>
                    <FormHelperText>
                        <div align="center">
                            Votes Required To Skip Song
                        </div>
                    </FormHelperText>
                </FormControl>
            </Grid>
            {props.update ? renderUpdateButtons() : renderCreateButtons()}
        </Grid>
    );
}

CreateRoomPage.defaultProps = {
    votes_to_skip: 2,
    guest_can_pause: true,
    update: false,
    code: null,
    updateCallback: () => {
    }
}

export default CreateRoomPage;



