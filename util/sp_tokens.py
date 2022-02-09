import time
import subprocess

import fire


def set_skyportal_admin_token(container_name="skyportal_web_1", container_token_file="/skyportal/.tokens.yaml",
                              local_token_file="./.tokens.yaml", token_identifier="INITIAL_ADMIN",
                              verbose=True, max_tries=10, max_time_allowed=600.0):
    """
    Grabs the admin token in the named container and stores it locally in a file
    cf. fritz/launcher/skyportal.py on the fritz-marshal/fritz project.

    Parameters
    ----------
    container_name : string
        The name of the running SkyPortal container
    container_token_file : string
        File path on the SkyPortal container with the token info
    local_token_file : string
        File path on the local machine where the token will be written
    token_identifier : string
        A valid token file should start with this in the first line
    verbose : bool
        Print out warnings and updates
    max_tries : int
        How many tries before giving up.
    max_time_allowed : float
        How many seconds before giving up.
    
    Returns
    -------

    Raises
    ------
    RuntimeError
        If we get a malformed token file or fail to pull the file over in the first place.

    """
    
    verbose = verbose in [True, 1, "t", "T"]

    def poll():
        tries = 0
        start_time = time.time()
        while tries < max_tries and time.time() - start_time < max_time_allowed:
            if verbose:
                print(f"[set_skyportal_admin_token] Trying to get token on try {tries+1}")
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "-i",
                    f"{container_name}",
                    "/bin/bash",
                    "-c",
                    f"cat {container_token_file}",
                ],
                cwd="skyportal",
                capture_output=True,
                universal_newlines=True,
            )
            if result.stdout:
                if result.stdout.find(token_identifier) != -1:
                    token = result.stdout.split()[-1]
                    if len(token) != 36:
                        raise RuntimeError(f"Failed to get a SkyPortal token. Got: {token}.")
                    return token
            else:
                if verbose and result.stderr:
                    print(f"Error: {result.stderr}")

            if tries < 5:
                time.sleep(10)
            else:
                time.sleep(3*tries)
            tries += 1

        raise RuntimeError(f"Failed to get a SkyPortal token after {tries} tries.")

    token = poll()
    if token:
        f = open(local_token_file, "w")
        f.write(f"{token_identifier}: {token}\n")
        f.close()
        if verbose:
            print(f"✨ Wrote {local_token_file} ✨") 


if __name__ == "__main__":
    fire.Fire(set_skyportal_admin_token)
