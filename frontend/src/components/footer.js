import {AppBar, Container, Toolbar} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";

export default function Footer() {
    return (
        <AppBar position="static" color="primary">
          <Container maxWidth="md">
            <Toolbar>
              <Typography variant="body1" color="inherit">
                © 2021 by Avi Gupta
              </Typography>
            </Toolbar>
          </Container>
        </AppBar>
    )
}