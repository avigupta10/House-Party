import {useEffect, useState} from 'react';
import {Button, Grid, Typography} from '@material-ui/core';
import {Tune} from '@material-ui/icons';
import CreateRoomPage from "./createroompage";
import MusicPlayer from "./musicplayer";
import Search from "./search"
import ListenerModal from "./Modal";


function Room(props) {
    const [votes_to_skip, setVotes] = useState(2)
    const [guest_can_pause, setPause] = useState(false)
    const [is_host, setHost] = useState(false)
    const [showSettings, setSettings] = useState(false)
    const [spotifyAuthenticated, setSpotifyAuthenticated] = useState(false)
    const [hostName, setHostName] = useState('')
    const [song, setSong] = useState({})

    const code = props.match.params.code;


    useEffect(() => {
        let interval = setInterval(getCurrentSong, 1000); //ComponentDidMount and  calling the function to get data stored in the variable
        return () => {                                            //ComponentWillUnmount
            clearInterval(interval)
        }
    }, [])


    const getRoomDetails = () => {
        fetch("/api/get-room" + "?code=" + code)
            .then((response) => {
                if (!response.ok) {
                    props.leaveRoomCallback();
                    props.history.push('/');
                }

                return response.json()
            })
            .then((data) => {
                setVotes(data.votes_to_skip);
                setPause(data.guest_can_pause);
                setHost(data.is_host);

                if (is_host) {
                    authenticateSpotify();
                }
            });
    }


    const authenticateSpotify = () => {
        fetch('/spotify/is-authenticated')
            .then((response) => response.json())
            .then((data) => {
                setSpotifyAuthenticated(data.status);
                if (!data.status) {
                    fetch('/spotify/get-auth-url')
                        .then((response) => response.json())
                        .then((data) => {
                            window.location.replace(data.url); // Redirecting to spotify_callback()
                        });
                }
            });
    }

    const getCurrentSong = () => {
        fetch('/spotify/current-song').then((response) => {
            if (!response.ok) {
                return {'Error': 'Play a song'};
            } else {
                return response.json();
            }
        }).then((data) => {
            setSong(data);
            setHostName(data.username)
        });
    }

    const leaveRoom = () => {
        const options = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
        };
        fetch('/api/leave-room', options).then((resp) => {
            props.leaveRoomCallback()
            props.history.push('/')
        });
    }

    function settingsPage() {
        return (
            <Grid container spacing={1} align="center">
                <Grid item xs={12}>
                    <CreateRoomPage update={true} guest_can_pause={guest_can_pause} votes_to_skip={votes_to_skip}
                                    code={code} updateCallback={getRoomDetails}/>
                </Grid>
                <Grid item xs={12}>
                    <Button color="secondary" variant="contained" aria-label="settings" onClick={() => {
                        settingsButtonClicked(false)
                    }}>
                        Close
                    </Button>
                </Grid>
            </Grid>
        );
    }

    function settingButton() {
        return (
            <Grid item xs={12} align="center">
                <Button color='primary' variant='contained' aria-label="settings" startIcon={<Tune/>} onClick={() => {
                    settingsButtonClicked(true)
                }}>
                    Settings
                </Button>
            </Grid>
        );
    }

    const settingsButtonClicked = (value) => {
        setSettings(value);
    };

    getRoomDetails(); // calling the function to get data stored in the variable

    if (showSettings) {
        return settingsPage();
    }

    function NoSongComponent() {
        return (
            <div>
                <Grid item xs={12} align='center'>
                    <Typography variant="p" component='p'>
                        <blockquote>
                            No Song is Playing From The Requested Spotify Account.Try To Play A Song And Refresh
                        </blockquote>
                    </Typography>
                </Grid>
                <Grid item xs={12}>
                    <Button color='secondary' variant='contained' onClick={leaveRoom}>
                        Leave Room
                    </Button>
                </Grid>
            </div>
        );
    }

    function SpotifyNotAuthenticated() {
        return (
            <div>
                <Grid item xs={12} align='center'>
                    <Typography variant="p" component='p'>
                        <blockquote>
                            Please Wait. You're Being Redirected to Spotify For Authentication
                        </blockquote>
                    </Typography>
                </Grid>
            </div>
        );
    }

    function MainRoomComponent() {
        return (
            <div>
                <Grid item xs={12} align='center'>
                    <ListenerModal song={song} hostName={hostName}/>
                </Grid>
                <Grid container spacing={1} align="center">
                    <Grid item xs={12} align="top">
                        <Typography variant="p" component='p'>
                            <blockquote>Logged in as {is_host ? hostName : song.guest_name} </blockquote>
                        </Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Search/>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography variant="h4" component='h4'>
                            Code: {code}
                        </Typography>
                    </Grid>
                    <MusicPlayer time={song.time} duration={song.duration} name={song.username} votes={song.votes}
                                 votes_required={song.votes_required} song_title={song.title}
                                 is_playing={song.is_playing} image_url={song.image_url} artist={song.artist}/>
                    {is_host ? settingButton() : null}
                    <Grid item xs={12}>
                        <Button color='secondary' variant='contained' onClick={leaveRoom}>
                            Leave Room
                        </Button>
                    </Grid>
                </Grid>
            </div>
        )
    }

    return (
        <Grid container spacing={1} align="center">
            {spotifyAuthenticated ? song.username ? MainRoomComponent() : NoSongComponent() : SpotifyNotAuthenticated() }
        </Grid>
    )
}

export default Room;



