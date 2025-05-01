# OpenValve Web App

This is a simple Flask app that performs several CRUD operations for the assignment. The design takes inspiration from the Steam UI.

## Viewing

Make sure poetry has installed dependencies with `poetry install`. Then run `make` to open the server.
It will be hosted on your local machine and available at `http://localhost:5000`

If you do not have poetry, use `pip install poetry`, or alternatively use `pipx` if you have it.
If you do not want to use poetry to manage dependencies, install the requisite libraries manually and run `make nopoetry` instead.

## Database configuration

Make sure to have a proper .env file as described in the parent folder's README
