import {Grid, Typography, Card, IconButton, LinearProgress} from "@material-ui/core";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import PauseIcon from "@material-ui/icons/Pause";
import SkipNextIcon from "@material-ui/icons/SkipNext";

function MusicPlayer(props) {
    const songProgress = (props.time / props.duration) * 100

    const pauseSong = () => {
        const options = {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
        }
        fetch('/spotify/pause-song', options)
    }

    const playSong = () => {
        const options = {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
        }
        fetch('/spotify/play-song', options)
    }

    const skipSong = () => {
        const options = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
        }
        fetch('/spotify/skip-song', options)
    };
    return (
        <Card>
            <Grid container spacing={1} align="center">
                <Grid item xs={4}>
                    <img src={props.image_url} height='100%' width='100%' />
                </Grid>
                <Grid item xs={8}>
                    <Typography component='h5' variant='h5'>
                        {props.song_title}
                    </Typography>
                    <Typography color='textSecondary' component='h5' variant='subtitle1'>
                        {props.artist}
                    </Typography>
                    <div>
                        <IconButton onClick={() => {props.is_playing ? pauseSong() : playSong()}}>
                            {props.is_playing ? <PauseIcon /> : <PlayArrowIcon />}
                        </IconButton>
                        <IconButton onClick={() => skipSong()}>
                            <SkipNextIcon />
                        </IconButton>
                        <Typography component='p' variant='p'>Votes required to skip: {props.votes} / {props.votes_required}</Typography>
                    </div>
                </Grid>
        </Grid>
            <LinearProgress variant='determinate' value={songProgress} />
        </Card>
    );
}

export default MusicPlayer;