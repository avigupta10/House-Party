import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Modal from '@material-ui/core/Modal';
import Backdrop from '@material-ui/core/Backdrop';
import Fade from '@material-ui/core/Fade';
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import StarIcon from "@material-ui/icons/Star";
import ListItemText from "@material-ui/core/ListItemText";
import List from "@material-ui/core/List";
import {Button} from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
    modal: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    paper: {
        backgroundColor: 'rgba(209, 222, 185, 0.99)',
        border: '2px solid #000',
        boxShadow: theme.shadows[5],
        padding: theme.spacing(2, 4, 3),
    },
}));

export default function ListenerModal(props) {
    const classes = useStyles();
    const [open, setOpen] = React.useState(false);

    const handleOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    return (
        <div>
            <Button color='primary' type='button' variant='outlined' aria-label="Listeners" onClick={handleOpen}>
                Listeners
            </Button>
            <Modal
                aria-labelledby="transition-modal-title"
                aria-describedby="transition-modal-description"
                className={classes.modal}
                open={open}
                onClose={handleClose}
                closeAfterTransition
                BackdropComponent={Backdrop}
                BackdropProps={{
                    timeout: 500,
                }}
            >
                <Fade in={open}>
                    <div className={classes.paper}>
                        <h2 id="transition-modal-title">Listeners</h2>
                        <List aria-label="Guests">
                            <ListItem button>
                                <ListItemIcon>
                                    <StarIcon/>
                                </ListItemIcon>
                                <ListItemText primary={props.hostName}/>
                            </ListItem>
                            {props.song.GUESTS && props.song.GUESTS.map((name) => {
                                return (<ListItem button><ListItemText inset primary={name}/></ListItem>)
                            })}
                        </List>
                    </div>
                </Fade>
            </Modal>
        </div>
    );
}