import {Fragment, useState} from "react";
import {Autocomplete} from "@material-ui/lab";
import CircularProgress from '@material-ui/core/CircularProgress';
import TextField from '@material-ui/core/TextField'


export default function Search() {
    const [songs, setSongs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [query, setQuery] = useState('');
    // const [uri, setURI] = useState('spotify:track:1zejeOnykpCoyVSit6Bwp3');

    const handleSearch = (e) => {
        const query = e.target.value;

        if (!query) {
            setQuery(query)
            setSongs([])
        } else {
            setQuery(e.target.value)
            setLoading(true)
            getSearchDetails(query)
        }
    }

    const playSearchSong = (uri) => {
        const options = {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({uris: uri})
        }
        fetch('/spotify/play-search', options)
    }


    async function getSearchDetails(query) {
        await fetch(`/spotify/search-song?query=${query}`).then((response) => response.json()
        ).then((data) => {
            setSongs(data)
        }).catch((error) => {
            setLoading(false)
        })
    }

    return (
        <Autocomplete
            id="combo-box-demo"
            options={songs}
            getOptionSelected={(option, value) => option.name === value.name}
            getOptionLabel={option => option.name}
            style={{width: 300}}
            loading={loading}
            onChange={(event, value) => {
                // setURI(value.uri)
                playSearchSong(value.uri)
                setLoading(false)
            }}
            renderInput={(params) => (
                <TextField
                    {...params}
                    label="Search Song"
                    variant="outlined"
                    onChange={handleSearch}
                    value={query}
                    InputProps={{
                        ...params.InputProps,
                        endAdornment: (
                            <Fragment>
                                {loading ? <CircularProgress color="inherit" size={20}/> : null}
                                {params.InputProps.endAdornment}
                            </Fragment>
                        ),
                    }}
                />
            )}
        />
    );
}